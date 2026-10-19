export function BackgroundPattern() {
  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
      {/* Light Mode Grid */}
      <svg
        className="absolute inset-0 h-full w-full dark:hidden"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="light-grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              className="text-slate-900/5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#light-grid)" />
      </svg>

      {/* Dark Mode Grid */}
      <svg
        className="absolute inset-0 h-full w-full hidden dark:block"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="dark-grid"
            width="40"
            height="40"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 40 0 L 0 0 0 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="0.5"
              className="text-white/[0.04]"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#dark-grid)" />
      </svg>


    </div>
  )
}
