def generate_peel_blank_board(output_path):
    svg_content = """<svg width="210mm" height="297mm" viewBox="0 0 210 297" xmlns="http://www.w3.org/2000/svg">
        <rect width="210" height="297" fill="#FFFFFF" />

        <text x="10" y="8" font-family="Arial" font-size="4" font-weight="bold" fill="#374151">ESSAY QUESTION:</text>
        <line x1="45" y1="8" x2="200" y2="8" stroke="#D1D5DB" stroke-width="0.3" />

        <rect x="10" y="15" width="190" height="35" rx="3" fill="#FFF1F2" stroke="#E85D4F" stroke-width="0.5" stroke-dasharray="2" />
        <text x="14" y="22" font-family="Arial" font-size="5" font-weight="bold" fill="#E85D4F">P — POINT (Argument + Judgement)</text>
        <text x="14" y="28" font-family="Arial" font-size="3" fill="#991B1B">What is your main claim? (Place L0 stickers here)</text>

        <rect x="10" y="55" width="190" height="85" rx="3" fill="#FFFBEB" stroke="#F59E0B" stroke-width="0.5" stroke-dasharray="2" />
        <text x="14" y="62" font-family="Arial" font-size="5" font-weight="bold" fill="#F59E0B">E — EVIDENCE (Specific Facts)</text>
        <text x="14" y="68" font-family="Arial" font-size="3" fill="#92400E">Support with L1 Events, L2 Actors, and L3 Institutions.</text>

        <rect x="10" y="145" width="190" height="95" rx="3" fill="#FAF5FF" stroke="#9333EA" stroke-width="0.5" stroke-dasharray="2" />
        <defs>
          <pattern id="dotGrid" x="0" y="0" width="10" height="10" patternUnits="userSpaceOnUse">
            <circle cx="5" cy="5" r="0.3" fill="#E9D5FF" />
          </pattern>
        </defs>
        <rect x="10" y="145" width="190" height="95" rx="3" fill="url(#dotGrid)" />
        <text x="14" y="152" font-family="Arial" font-size="5" font-weight="bold" fill="#9333EA">E — EXPLAIN (Causal Linkage)</text>
        <text x="14" y="158" font-family="Arial" font-size="3" fill="#6B21A8">Connect Evidence to Argument using MECHANISM tags & arrows.</text>

        <rect x="10" y="245" width="190" height="42" rx="3" fill="#F9FAFB" stroke="#6B7280" stroke-width="0.5" stroke-dasharray="2" />
        <text x="14" y="252" font-family="Arial" font-size="5" font-weight="bold" fill="#374151">L — LINK (Back to Question)</text>
        <text x="14" y="258" font-family="Arial" font-size="3" fill="#4B5563">Summarize how this paragraph answers the essay prompt.</text>
    </svg>"""
