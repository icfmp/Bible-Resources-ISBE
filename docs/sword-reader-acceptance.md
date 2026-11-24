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
startup, headword lookup, screenshot capture, and an actual pointer-click
probe** on a visible `Ex 6:20` link in AARON for each reader. The probe
uses observed positions under the fixed 1440×900 Xvfb fixture; it is **not**
a portable GUI locator. Its before/after window titles, pointer-event result,
fixed screen coordinates, and post-click PNG are diagnostics. The script
explicitly labels **link navigation unverified** because sending a click and
capturing a changed image does not certify the destination. A reviewer must
compare the before/after screenshots, verify the opened Bible module and
exact passage, and record success or failure separately. Recalibrate any
coordinates after a client UI/layout change; do not weaken the assertion.
Intra-encyclopedia hyperlink clicks are still a distinct acceptance gate.

### BibleTime fresh-profile Scripture link prerequisite

A real click on the source-attested `Ex 6:20` hyperlink was observed in the
unconfigured BibleTime fresh profile, but displayed **Choose Standard Bible**
instead of opening the passage (PR #89, run #45337526910, attempt 2).
Upstream BibleTime `BtConfig` reads settings from
`$HOME/.bibletime/bibletimerc`, and
`getDefaultSwordModuleByType("standardBible")` expects the Qt INI key
`settings/defaults/standardBible`. Its configuration migration API version
must be `btconfig_api_version=1`. The dedicated GUI workflow now seeds
**only the temporary HOME** with the **actual installed SWORD module ID** of the public-domain
King James *test fixture* (currently `engKJV2006eb` on Ubuntu, not `KJV`)
as `standardBible` and retains the click and screenshot checks. The
configured ID is discovered through `diatheke` rather than hardcoded. This does not
introduce any KJV dependency into the curated ISBE candidate.

The BibleTime standard Bible configuration is a **setup prerequisite**,
not a passing hyperlink navigation result. With the actual installed King
James module ID configured, the first independent screenshot shows a BibleTime
window titled **Exodus 6:20** and its reference pane displaying the requested
verse, **but the main Bible body still displays Genesis 1**. Therefore the
passage-body gate is **NOT yet certified**. The GUI probe now records a second,
settled screenshot eight seconds later to distinguish transient rendering
from a lasting reader navigation failure. Review both screenshots and only
accept the exact visible Exodus 6:20 **body** when genuinely shown. Xiphos's click to a local missing `/passagestudy.jsp`
file is a separate client/filter routing problem; it must not be concealed
by modifying historical `cRef` / `osisRef` source links.

Do not add guessed content to make a GUI test pass.

## Release boundary

Successful native SWORD validation and two-reader GUI checks do not grant
copyright or redistribution clearance. Keep publication and catalog changes
blocked until the source-specific rights review and owner sign-off are
completed. Preserve original source and corrected historical master bytes.
