# International Standard Bible Encyclopedia (1915) — Bible Resources 0.1.0

The first public **historically corrected English ISBE** release from [Bible Resources ISBE](https://github.com/icfmp/Bible-Resources-ISBE).

This is an **annotated, source-traceable digital edition**, **not** a complete facsimile or exhaustive five-volume printed collation.

## Contents

- **9,380** independently compiled and fully read-back SWORD dictionary entries, module ID `BRISBE1915`, driver `zLD`, ZIP compression, UTF-8.
- **31** originally empty digital entries recovered from documented 1915 print evidence (20 textual entries and 11 redirects); additional source-attested, reversible corrections are preserved.
- **5,919** original internal dictionary cross-references exported to actual `BRISBE1915:<article key>` targets rather than the invalid `self:<article key>` SWORD work name. Original source `#xml:id` selectors remain in the generated adapter's `corresp`.
- **93,164** Bible reference fields exposed as native `osisRef` values, while the original reference fields and printed labels are preserved.
- Complete **9,380/9,380** libSWORD `mod2imp` native roundtrip with **zero missing/extra entries, zero Unicode text differences, and zero XML structure differences**.
- Original CrossWire 2.2 source archived unchanged in Git; corrected historical TEI P5 master validated against the official schema and immutably SHA-pinned.

## Downloads

- `BRISBE1915-0.1.0-SWORD.zip` — **recommended SWORD package** for compatible readers; contains `mods.d/brisbe1915.conf` and `modules/lexdict/zld/brisbe1915/`.
- `BRISBE1915-0.1.0-SWORD.tar.gz` — exactly the same independently validated binary tree as the internally staged candidate (the upstream draft asset is checksum-pinned).
- `BRISBE1915-0.1.0-source.zip` — corrected historical TEI master, original provenance/manifests, scoped editorial assessment and source README.
- `BRISBE1915-0.1.0-SHA256SUMS.txt` — SHA-256 checksums for all three archives.

Import the SWORD ZIP through a SWORD-compatible installation mechanism, or extract the module archive to a temporary directory and install its `mods.d` and `modules` files in your SWORD data directory. Do not overwrite the original upstream CrossWire `ISBE` module: this release installs under a **different** module ID.

## Verified fidelity and reader tests

- Native source-to-SWORD and full binary roundtrip, all entries: [current corrected native build](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45347402944).
- Real dictionary link `ARK → ARK OF BULRUSHES` tested in Xiphos and BibleTime: [two-reader evidence](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45344977265).
- Greek in `CHORBE`, pointed Hebrew in `AMNON`, and numbered nested subdivisions in `ELKOSHITE` independently inspected in both graphical readers: [GUI screenshots](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111541).
- Full automated paratext screening of **9,380** articles in both source witnesses: **zero source-attested non-content digitization notices detected** by specific patterns. The separately reviewed 21 broad keyword candidates were retained as historical prose. [Audit run](https://github.com/icfmp/Bible-Resources-ISBE/actions/runs/45349111567), [assessment](https://github.com/icfmp/Bible-Resources-ISBE/blob/main/workspace/reviews/isbe-1915-publication-editorial-assessment.md).

## Known limitations — read before use

1. **Xiphos:** the clicked dictionary cross-reference resolves to the correct destination in the **dictionary Viewer**, but its separate **Book View** can still show “The URL can't be shown”.
2. **BibleTime:** the destination is visible in the **Mag** pane. Some Bible-reference clicks can open the requested reference title without the main Bible text pane immediately displaying the requested passage; Xiphos's Scripture navigation is also imperfect. These are not silently “corrected” by changing historical Bible references.
3. **80** source references target positions inside an article; native SWORD dictionary navigation reaches the **containing article**, without guaranteed exact internal scrolling. Exact source `#xml:id` anchors are retained in the historical TEI and generated import.
4. Some duplicate-looking article titles are the reader's own dictionary key shown next to the **unchanged, original authorial heading**.
5. Original 1915 printed Greek/Hebrew typography and all five printed volumes were **not** exhaustively collated against this digital witness. The edition's source-present Greek/Hebrew characters and retained structures are verified, not every character in the historical printed books.

No correction has been invented to make a GUI test pass. Future editorial fixes must be source-attested, reviewable, reversible and published as **new versions**, never silently replacing these 0.1.0 bytes.

## Provenance and redistribution

- Edition: *International Standard Bible Encyclopedia*, original 1915 historical publication; digitization basis CrossWire ISBE 2.2.
- Upstream module distribution declaration: **Public Domain**. The project owner accepts this designation as the basis for distributing the reviewed edition.
- Original CrossWire archive SHA-256: `4de747545d9c349ab724bc1708b01df5481e3b93e5e51077f859dd8a32023a32`.
- Corrected historical TEI SHA-256: `5df8a6d1311e3f5a83a6d961c6e09c27e042b0c68b4a9da54cb98821cb878d2c`.
- Exact native SWORD importer TEI SHA-256: `bdac245cad329fdff8039d0374815ff7086b8a5f8055118f1250461b9d5f17ec`.
- Pinned, independently validated internal draft SWORD tarball SHA-256: `6b7edccc0f27fbcf71595597ddd8794a5db72acd3952fb03e1e4e569e7acf3a5`.

The original CrossWire binary/digital source and corrected historical edition remain distinguishable in the repository; no upstream original has been overwritten.
