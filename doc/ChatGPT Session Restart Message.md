🧵 Ending Chat 10 → Starting Chat 11

Chat 10: XLIFF 2.0 Validation 10 (complete)

Chat 11: XLIFF 2.0 Validation 11 (next)

Zip Version: xliff_validator_v10.zip

Structure: Original layout with /src, /test-files, /generated-files, and /doc

✅ Canvas Setup

Canvas Name Type Preload With Permissions

Check Function code/python Active Python script ✅ Editable by ChatGPT

Output Viewer document Empty ✅ Editable by ChatGPT

⚙️ Setup Instructions

Delete everything in /mnt/data except the uploaded zip.

Extract using system command only (Python ziplib causes file corruption):

unzip /mnt/data/xliff_validator_v10.zip -d /mnt/data

Load check_duplicate_ids.py from /mnt/data/src/checks/ into the Check Function canvas.

Do not hallucinate or generate code — read directly from disk.

Confirm that the canvas matches the actual file contents.

When I say to run a test:

Use validate_xliff_file() on a test file like:

/mnt/data/test-files/MCB_OTPS_L01_Storyline(en).xlf

All results must go only to the Output Viewer (never chat). Follow the markdown format from doc/Output Viewer Sample.md

🧪 Output Viewer Format Must Include:

Script Output (print log of which checks ran, in order, showing version numbers)

Test Results Table (file, count, first few messages)

Validation Issues Table (one row per issue — fill in all columns)

Highlighted Line Snippets (one per issue listed above)

Test Rule Summary for Check #7 (current check focus)

Failure File Definitions (optional if not testing failure cases)

Use ✅ or ❌ for each check header depending on whether it passed or failed.

📏 ChatGPT Rules
Review all documentation /mnt/data/docs. It contains knowledge you'll need. However, some of it is outdated, so if there's a conflict between what's there and this message, then use what's in this message.
Review and validate all code in /mnt/data/src. Make an internal map of which files have which functions and classes in them so you know where to look when needed.
When tests are run, use the files in /mnt/data/test-files
Responses in chat must stay short to avoid chat bloat and having the chat become unresponsive and eventually the environment resetting and losing all work
All output from running this code always to the Output Viewer, NEVER chat
Use proper test result tables, validator names, file paths, etc.
Read the contents of the Output Window afterwards to check the results of the run.
If something fails, add diagnostics to the Output Window of what went wrong and what you think needs to be done to fix it.
Always confirm which checks ran — don’t assume success
Always check your work. Do some things to validate that what you think you did actually happened. If you say you changed the canvas, check it afterwards to make sure it's valid Python and your changes are there. If you say you created a file, check that file to ensure it exists and the content is what you thought it should be. If you run a test, check the output to be sure the output matches what is expected.
When editing functions, they have a debug statement with a function version number in them. If you change them, increment that version number. Always check the output of runs to ensure all functions ran, in order, and have the right version number printed (that matches the source code).
Validation checks are in the /mnt/data/src/checks subfolder and each py file contains a function of the same name.

🧪 Test File Notes

All .xlf files in /mnt/data/test-files/ are known good.

If any check fails, it means the check logic is broken.

Use failure cases only when explicitly instructed and generate them on-demand.












