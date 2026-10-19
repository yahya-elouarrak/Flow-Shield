import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from sqlmodel import Session, select
import os
from jinja2 import Environment, FileSystemLoader

from app.db.session import get_session
from app.models.project import Project, TargetConfig
from app.models.openapi import Endpoint
from app.models.scan_models import ScanJob, TestCase, TestExecution
from app.models.finding_models import Finding, Evidence

router = APIRouter()

# Setup Jinja2 Environment
templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
env = Environment(loader=FileSystemLoader(templates_dir))

import json

def chunk_text_for_pdf(text, max_lines=28, max_chars_per_line=110):
    if not text:
        return []
        
    if isinstance(text, (dict, list)):
        text = json.dumps(text, indent=2)
    elif isinstance(text, str):
        try:
            parsed = json.loads(text)
            text = json.dumps(parsed, indent=2)
        except Exception:
            pass
            
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    
    for line in lines:
        current_chunk.append(line)
        if len(current_chunk) >= max_lines:
            chunks.append('\n'.join(current_chunk))
            current_chunk = []
            
    if current_chunk:
        chunks.append('\n'.join(current_chunk))
        
    return chunks

env.filters['chunk_text'] = chunk_text_for_pdf

def gather_report_data(session: Session, project_id: Optional[uuid.UUID] = None, scan_id: Optional[uuid.UUID] = None):
    # Retrieve the ScanJob
    if scan_id:
        scan = session.get(ScanJob, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        project = session.get(Project, scan.project_id)
    elif project_id:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        # Get latest completed scan
        scan = session.exec(
            select(ScanJob)
            .where(ScanJob.project_id == project_id)
            .where(ScanJob.status == "completed")
            .order_by(ScanJob.created_at.desc())
        ).first()
        if not scan:
            raise HTTPException(status_code=404, detail="No completed scans found for this project")
    else:
        raise HTTPException(status_code=400, detail="Must provide project_id or scan_id")

    # Target Config
    target_config = session.exec(select(TargetConfig).where(TargetConfig.project_id == project.id)).first()
    
    # Endpoints count
    endpoints = session.exec(select(Endpoint).where(Endpoint.project_id == project.id)).all()
    total_endpoints = len(endpoints)
    
    # Tests Generated
    total_tests = session.exec(
        select(TestCase).where(TestCase.scan_id == scan.id)
    ).all()
    
    # Findings
    findings_records = session.exec(
        select(Finding).where(Finding.scan_id == scan.id)
    ).all()
    
    # Attach evidence to findings for report
    findings_data = []
    has_critical = False
    has_high = False
    for f in findings_records:
        evidence = session.exec(select(Evidence).where(Evidence.finding_id == f.id)).first()
        f_dict = f.dict()
        f_dict["evidence"] = evidence.dict() if evidence else None
        findings_data.append(f_dict)
        if f.severity.lower() == "critical":
            has_critical = True
        elif f.severity.lower() == "high":
            has_high = True
            
    overall_risk = "Low"
    if has_critical:
        overall_risk = "Critical"
    elif has_high:
        overall_risk = "High"
    elif len(findings_records) > 0:
        overall_risk = "Medium"

    return {
        "project": project,
        "scan": scan,
        "target_config": target_config or {"allowed_hosts": [], "allowed_paths": []},
        "total_endpoints": total_endpoints,
        "total_tests": len(total_tests),
        "total_findings": len(findings_records),
        "overall_risk": overall_risk,
        "findings": findings_data
    }


from fastapi.encoders import jsonable_encoder

def generate_json_report(data: dict):
    # Convert SQLModel objects to dicts for JSON serialization using jsonable_encoder
    json_data = {
        "project": jsonable_encoder(data["project"]),
        "scan": jsonable_encoder(data["scan"]),
        "target_config": jsonable_encoder(data["target_config"]),
        "metadata": {
            "total_endpoints": data["total_endpoints"],
            "total_tests": data["total_tests"],
            "total_findings": data["total_findings"],
            "overall_risk": data["overall_risk"]
        },
        "findings": jsonable_encoder(data["findings"])
    }
    return JSONResponse(content=json_data)


# -- PDF Helper --
def generate_pdf_from_html(html_content: str) -> bytes:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        footer_template = """
        <div style="font-size:9px;width:100%;padding:0 14mm;color:#6b7280;display:flex;justify-content:space-between;">
          <span>FlowShield Security Report</span>
          <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
        </div>
        """
        
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=footer_template,
            margin={
                "top": "18mm",
                "right": "14mm",
                "bottom": "18mm",
                "left": "14mm"
            }
        )
        browser.close()
    return pdf_bytes

# -- Project Level Routes --

@router.get("/projects/{project_id}/reports/html", response_class=HTMLResponse, tags=["reports"])
def get_project_report_html(project_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, project_id=project_id)
    template = env.get_template("report.html")
    html_content = template.render(**data)
    return HTMLResponse(content=html_content)

@router.get("/projects/{project_id}/reports/json", tags=["reports"])
def get_project_report_json(project_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, project_id=project_id)
    return generate_json_report(data)

@router.get("/projects/{project_id}/reports/markdown", response_class=PlainTextResponse, tags=["reports"])
def get_project_report_markdown(project_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, project_id=project_id)
    template = env.get_template("report.md")
    md_content = template.render(**data)
    return PlainTextResponse(content=md_content)

@router.get("/projects/{project_id}/reports/pdf", tags=["reports"])
def get_project_report_pdf(project_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, project_id=project_id)
    template = env.get_template("report_pdf.html")
    html_content = template.render(**data)
    pdf_bytes = generate_pdf_from_html(html_content)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=flowshield_report.pdf"})


# -- Scan Level Routes --

@router.get("/scans/{scan_id}/reports/html", response_class=HTMLResponse, tags=["reports"])
def get_scan_report_html(scan_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, scan_id=scan_id)
    template = env.get_template("report.html")
    html_content = template.render(**data)
    return HTMLResponse(content=html_content)

@router.get("/scans/{scan_id}/reports/json", tags=["reports"])
def get_scan_report_json(scan_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, scan_id=scan_id)
    return generate_json_report(data)

@router.get("/scans/{scan_id}/reports/markdown", response_class=PlainTextResponse, tags=["reports"])
def get_scan_report_markdown(scan_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, scan_id=scan_id)
    template = env.get_template("report.md")
    md_content = template.render(**data)
    return PlainTextResponse(content=md_content)

@router.get("/scans/{scan_id}/reports/pdf", tags=["reports"])
def get_scan_report_pdf(scan_id: uuid.UUID, session: Session = Depends(get_session)):
    data = gather_report_data(session, scan_id=scan_id)
    template = env.get_template("report_pdf.html")
    html_content = template.render(**data)
    pdf_bytes = generate_pdf_from_html(html_content)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=flowshield_scan_{str(scan_id)[:8]}.pdf"})

