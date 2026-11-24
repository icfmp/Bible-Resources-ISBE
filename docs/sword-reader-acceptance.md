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

### Verified native TEI dictionary link behavior

The CrossWire [TEI Dictionary guide](https://wiki.crosswire.org/TEI_Dictionaries)
documents `target="self:key"` for same-dictionary references, but the
SWORD 1.9 [TEIHTMLHREF implementation](https://crosswire.org/svn/sword/trunk/src/modules/filters/teihtmlhref.cpp)
splits targets at the first colon and treats the left component as a literal
module ID. Hence `self:key` renders as `sword://self/key`, which Xiphos
could not open during [real-click run #45343687175](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45343687175).
The native adapter now takes an **explicit installed SWORD module ID** and
rewrites original `#xml:id` references to `BRISBE1915:key`; the exact
original selector remains in `corresp`. This maps to the standard
`sword://BRISBE1915/key` URL in the SWORD TEI renderer, even for dictionary
keys that contain a colon. The historical TEI source is not altered.
**Both real-reader click destinations must be reconfirmed on the rebuilt
candidate before declaring compatibility.**

### Internal encyclopedia hyperlink fixture inventory

The reusable `scripts/select_isbe_internal_link_samples.py` independently
locates **source-attested article-to-article TEI links**, verifies the exact
original selector against the source-to-SWORD adapter and ranks candidate
source articles whose first clickable reference is an internal dictionary
link near the article opening. The report includes source/destination keys,
original `#xml:id`, mapped `self:` key, link text and text offset, without
altering the source. The native diagnostic artifact retains 25 candidates.

The two-reader smoke now makes a real lookup of the top ranked candidate in
both graphical readers, captures **its source article before a link click**,
then restores AARON and continues the existing Bible-reference probe. These
new candidate screenshots establish reproducible clickable coordinates.
The captured real-reader [run #45343260274](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45343260274)
shows the source-attested **ARK** entry and its grey/blue
**ARK OF BULRUSHES** hyperlink in both independent readers. The fixture
`tests/fixtures/isbe-gui-internal-link-click.json` stores the exact
screen points *observed in those real images*, not guessed locations.
The automated probe sends actual mouse events to those points and captures
after-click screenshots, but **does not pre-certify** the destination article
body. If the source/destination sample changes, the workflow fails rather
than silently clicking a different link. The
`interactive_dictionary_to_dictionary_link_verified` marker stays `false`
until the resulting screenshots are independently reviewed.

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

For **ISBE 1915**, the owner has explicitly accepted CrossWire's declared
Public Domain status and the historical edition as the project's distribution
basis; no further jurisdiction-specific rights audit is a release prerequisite.
This is not a claim that one was carried out. Publication and catalogue changes
still require completion or documented acceptance of outstanding technical and
editorial reader limitations, and owner authorization of the actual release.
Preserve original source and corrected historical master bytes.


### Independently reviewed real-reader result — 2026-11-24

The complete native / official-schema / Xiphos / BibleTime checks for the
explicit-work adapter are in [PR #95](https://github.com/icfmp/Bible-Resources-ISBE/pull/95)
and [GUI run #45344977265](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45344977265).
The actual `ARK` → `ARK OF BULRUSHES` source-attested hyperlink was clicked
with a real X11 pointer event in both readers, using the previously recorded
source-article screenshots.

- **BibleTime 3.2.0:** after the click, the *Mag* pane shows the exact
  `ARK OF BULRUSHES` heading and matching article prose. The main document
  includes both the ARK entry and the beginning of the linked entry. The
  screenshot proves a usable destination in the Mag pane, not necessarily a
  fresh main-document lookup.
- **Xiphos:** after the click, the *left dictionary Viewer* changes to
  `BRISBE1915: ARK OF BULRUSHES` and displays actual destination article
  prose. This confirms that `BRISBE1915:<key>` resolves to the installed
  dictionary. However the separate right *Book View* displays
  **"The URL can't be shown"** rather than a clean destination article.
  This is a separate GUI view/routing limitation still requiring review.

The compiled SWORD HTMLHREF output uses
`sword://BRISBE1915/ARK+OF+BULRUSHES` (URL-encoded `+` spaces), now covered
by an independent real native-renderer check in the workflow. The full native
roundtrip remains source-faithful: 9,380 entries, 5,919 internal targets,
93,164 Bible reference fields and zero text/structure mismatches. The
historical corrected TEI and source IDs are unchanged. **Do not describe
Xiphos Book View navigation as fully accepted** or claim the click resolves
every entry without separate evidence.

The **latest unpublished draft candidate** (`BRISBE1915-native-workid-draft.tar.gz`, SHA-256
`6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5`) now contains the corrected explicit `BRISBE1915:<key>`
crosslinks, rebuilt and verified by [run #45346863700](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45346863700).
The earlier superseded draft binary, retained for provenance, still has the
old `self:<key>` links and must not be used for eventual publication.

## Additional public-candidate presentation samples (2026-11-24)

The source-attested [script/structure census](../scripts/audit_sword_presentation_samples.py) selects **CHORBE** (Greek characters at source text offset 15), **AMNON** (pointed Hebrew at offset 14) and **ELKOSHITE** (one nested TEI division) from the locked corrected master. The graphical workflow makes real dictionary lookups of all three keys in *both* independent clients and retains six separately named screenshots. Each lookup is cross-checked against the source inventory before execution; an image file is evidence of a real opened UI, not an automatic certification of correct script glyphs or nested section rendering. Independent screenshot review is required and is recorded separately.

Historical original print glyph restoration is still not claimed: the census tests preservation of characters **present in the corrected digital witness**, not the completeness of the 1915 print transcription. The original TEI remains immutable.

### Independent review of six reader screenshots — 2026-11-24

[GUI run #45349111541](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111541), artifact `BRISBE1915-Xiphos-BibleTime-reader-diagnostics` (ID `14899706367`) includes **six actual screenshots** of the native candidate built from the SHA-pinned corrected TEI master. The images were independently inspected after the runner successfully opened and looked up each article:

| Attested source sample | Xiphos | BibleTime | Limit |
| --- | --- | --- | --- |
| `CHORBE` (Greek `Χορβέ`, source offset 15) | Original Greek glyphs visible in dictionary pane | Original Greek glyphs visible in main lexicon pane | Only script actually present in the corrected digital source verified |
| `AMNON` (pointed Hebrew, source offset 14) | Hebrew glyphs and vocalization visible; article prose legible | Hebrew glyphs and vocalization visible; article prose legible | No claim of exhaustive right-to-left typographic or printed-edition parity |
| `ELKOSHITE` (nested TEI division) | Article prose and numbered internal subsections visible | Article prose and numbered internal subsections visible | Single representative nested article, not all 29 |

The Greek and Hebrew text is readable in both independent readers; the nested example retains its (1)–(3) and (a)–(c) subsection markers in the displayed prose. Headwords may appear duplicated because readers display their own key adjacent to the author's preserved article heading; BibleTime often displays neighboring dictionary articles in the same document. These are reader presentation choices, **not permission to delete original headings**.

The complete source-to-native census independently verifies exactly **11 articles containing Greek codepoints, 10 containing Hebrew codepoints, and 29 containing nested divisions** in the corrected digital witness; all source-attested Unicode characters and nested TEI elements survive the import. This is **not** evidence that every Greek/Hebrew form present in the printed 1915 volumes was recovered from the upstream digitization. Remaining client-specific Bible-reference navigation and Xiphos Book View limitations are described above and should be disclosed in the eventual release.
