# 🤖 AI Operational Shortcuts

When the user provides a command in the format "Review [ID]" (e.g., "Review E049"):

1. **LOCATE:** Search the `/archive` directory for any file matching `*[ID]*Transcript.md`.
2. **LOAD CONTEXT:**
   - Read `BRAND-VOICE.md` for persona rules.
   - Read `Templates/Feedback-Template.md` for the audit structure.
3. **EXECUTE:** Perform a clinical audit of the located transcript using the rules in the Feedback Template.
4. **OUTPUT:** Provide the results in the exact format defined in the "FEEDBACK OUTPUT FORMAT" section of the template.