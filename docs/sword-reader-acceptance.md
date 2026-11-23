# Independent SWORD graphical-reader acceptance

This procedure distinguishes **native corpus parity**, **module discovery**,
**visible article rendering**, and **actual interactive navigation**. These
are independent gates; a successful startup is never proof of the others.

## Reader environment

- Use two independently packaged SWORD GUI front ends (currently Xiphos and
  BibleTime), record their exact versions and the SWORD library version.
- Verify source SHA-256 and native SWORD `mod2imp` parity *before* GUI checks.
- Run against a temporary, writable `HOME`, XDG directories and D-Bus/X11
  session. Do not use your normal SWORD installation or inadvertently overwrite
  an existing module.
- Xiphos requires a genuine Bible text to initialize a fresh profile. The
  distribution-provided KJV may serve **only as an isolated test fixture**, not
  as a dependency or file in the curated dictionary release.
- BibleTime deliberately unsets `SWORD_PATH` during startup. Install the
  candidate's `mods.d/` and `modules/` trees into the isolated
  `$HOME/.sword/` root before launching BibleTime. Independently verify
  `env -u SWORD_PATH diatheke -b system -k modulelist` sees the expected
  module under *Lexicons / Dictionaries*. The exact discovery path matters:
  an Xiphos success using `SWORD_PATH` is not a BibleTime acceptance.
- Verify the candidate's SWORD module name, data root, encoding, module
  driver, TEI source type and nonpublication/rights metadata separately.

References: [BibleTime directory implementation](https://bibletime.info/api_docs/d3/d62/directory_8cpp_source.html)
explicitly unsets `SWORD_PATH` (source lines 90–91); see also the
[CrossWire SWORD module configuration guide](https://wiki.crosswire.org/DevTools:conf_Files).

## Independent acceptance levels

1. **Discovery:** native SWORD and the *actual application's* library list
   recognize the expected dictionary module, not merely the KJV test Bible.
2. **Article display:** open at least one known source-key article from the
   GUI, record its exact displayed title and sample content, and inspect
   screenshots for actual prose/paragraph structure. Capturing the program's
   Welcome dialog or an empty work area is insufficient.
3. **Article navigation:** move to a different source article key through
   the GUI; confirm the displayed body actually changed.
4. **Interactive references:** click representative internal article links
   and Bible references; verify the resulting destination, not just that an
   HTML `href` string exists in a native renderer.
5. **Editorial presentation:** inspect original-language text where
   source-attested (Greek/Hebrew), titles, paragraph structure, nested
   sections, references and intentional editorial fixes. Document any
   client-specific losses separately from source changes.
6. **Regression and provenance:** retain the exact CI run, commit SHA, module
   digest, output report and an honest statement of *which* acceptance gates
   passed. Avoid binary distribution through public Actions artifacts.

The reusable `scripts/smoke_sword_gui_readers.py` performs **automated
startup and screenshot capture** only. It deliberately labels article
rendering and link clicks *uncertified*. Interactive GUI acceptance requires
inspection of those screenshots and evidence of actual user interaction.
Do not add guessed content to make a GUI test pass.

## Release boundary

Successful native SWORD validation and two-reader GUI checks do not grant
copyright or redistribution clearance. Keep publication and catalog changes
blocked until the source-specific rights review and owner sign-off are
completed. Preserve original source and corrected historical master bytes.
