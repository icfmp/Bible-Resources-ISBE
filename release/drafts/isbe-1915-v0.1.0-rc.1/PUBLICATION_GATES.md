# Rights and editorial gates for ISBE 1915 v0.1.0-rc.1

**Outcome: DO NOT PUBLISH.** A source-pinned internal GitHub release *draft* may be staged, but no release publication is authorized by technical validations.

## Verified

- [x] CrossWire ISBE 2.2 source retained as an immutable ZIP with exact SHA-256 and upstream attribution.
- [x] CrossWire **declares** `DistributionLicense=Public Domain` for the module, confirmed at https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=ISBE and in the archived module configuration.
- [x] The 1915 Orr/Howard-Severance print is an original historical source; pre-1931 U.S. publication is public domain in the U.S.
- [x] The corrected 9,380-entry historical TEI is separately pinned and can be reconstructed byte-for-byte with original evidence and official TEI P5 schema validation.
- [x] Cleaned edition, source-faithful CrossWire witness and original ZIP are distinctly stored and identified; no SWORD package has been published.

## Unresolved before publication

- [ ] Establish the law applicable to distinct named ISBE article contributors in the **EU/France**. A multi-author encyclopedia is not automatically exempt from protection on identifiable separately authored articles merely because the U.S. printed original is in the public domain. Check whether French *œuvre collective* rules apply to the work as a whole and whether individual contributions retain separate protection.
- [ ] Verify the exact chain and basis of CrossWire 2.2 digital *text / markup / later OCR corrections*, including contributions not in the original 1915 edition.
- [ ] Confirm whether the rights situation of the exact digitally edited TEI is sufficient for unrestricted redistribution in target countries, not merely for preserving working files in Git.
- [ ] Independently check contributor and publisher notices/attribution before distributing a new SWORD module, modernized derivative or translation.
- [ ] Obtain final owner-approved editorial and distribution sign-off (including source display, native SWORD reader acceptance if a compiled module is contemplated). This draft is TEI **source only**.

## References

- CrossWire module metadata: https://www.crosswire.org/sword/modules/ModInfo.jsp?modName=ISBE
- CrossWire copyright metadata: https://crosswire.org/sword/copyright/ModInfoCopyright.jsp?modName=ISBE
- CrossWire's general module copyright policy: https://wiki.crosswire.org/Copyright
- Official French copyright terms, particularly L123-1 and L123-3: https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006069414/LEGISCTA000006161638/
- Original 1915 volume facsimile attribution (U.S. public-domain claim): https://commons.wikimedia.org/wiki/File:The_International_Standard_Bible_Encyclopedia_Volume_1.pdf
- Project rights tracking: https://github.com/icfmp/Bible-Resources-ISBE/issues/1

**Fail closed**: no automatic workflow may call `gh release edit --draft=false`, upload a public artifact, promote a tag to a published release, or claim the remaining gates passed without separate review and authorization.
