"""
source_registry.py — Central registry mapping bibliography keys to download sources.

Each entry in references.bib is mapped to:
  - Ancient/Patristic: public domain URLs for downloading full text
  - Modern: instructions for obtaining copyrighted works

Usage:
    from source_registry import SOURCES, get_sources_by_category
"""

# Categories
ANCIENT = "ancient"
PATRISTIC = "patristic"
MODERN = "modern"

SOURCES = {
    # =========================================================================
    #  ANCIENT PRIMARY SOURCES
    # =========================================================================

    "josephus:war": {
        "title": "The Jewish War",
        "author": "Flavius Josephus",
        "category": ANCIENT,
        "translation": "William Whiston (1895)",
        "urls": {
            "book1": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D1",
            "book2": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D2",
            "book3": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D3",
            "book4": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D4",
            "book5": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D5",
            "book6": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D6",
            "book7": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0148%3Abook%3D7",
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "josephus:ant": {
        "title": "Jewish Antiquities",
        "author": "Flavius Josephus",
        "category": ANCIENT,
        "translation": "William Whiston (1895)",
        "urls": {
            f"book{i}": f"https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0146%3Abook%3D{i}"
            for i in range(1, 21)
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "josephus:apion": {
        "title": "Against Apion",
        "author": "Flavius Josephus",
        "category": ANCIENT,
        "translation": "William Whiston (1895)",
        "urls": {
            "book1": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0216%3Abook%3D1",
            "book2": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0216%3Abook%3D2",
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\.\s)",
    },

    "josephus:life": {
        "title": "Life of Flavius Josephus",
        "author": "Flavius Josephus",
        "category": ANCIENT,
        "translation": "William Whiston (1895)",
        "urls": {
            "full": "https://lexundria.com/j_vit/1-430/wst",
        },
        "section_pattern": r"\b(\d+)\b",
    },

    "tacitus:annals": {
        "title": "Annals",
        "author": "Cornelius Tacitus",
        "category": ANCIENT,
        "translation": "Alfred John Church and William Jackson Brodribb (1876)",
        "urls": {
            "book1": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/1A*.html",
            "book11": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/11A*.html",
            "book12": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/12A*.html",
            "book13": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/13A*.html",
            "book14": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/14A*.html",
            "book15": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/15A*.html",
            "book15b": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/15B*.html",
            "book16": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Annals/16*.html",
        },
        "alt_urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0078",
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "tacitus:histories": {
        "title": "Histories",
        "author": "Cornelius Tacitus",
        "category": ANCIENT,
        "translation": "Alfred John Church and William Jackson Brodribb (1876)",
        "urls": {
            "book1": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/1A*.html",
            "book2a": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/2A*.html",
            "book2b": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/2B*.html",
            "book3": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/3A*.html",
            "book4": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/4A*.html",
            "book5": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Tacitus/Histories/5A*.html",
        },
        "alt_urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0080",
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\.\s)",
    },

    "suetonius:claudius": {
        "title": "Life of Claudius",
        "author": "Gaius Suetonius Tranquillus",
        "category": ANCIENT,
        "translation": "J. C. Rolfe (Loeb, 1914)",
        "urls": {
            "full": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Claudius*.html",
        },
        "alt_urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0132%3Alife%3Dcl.",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "pliny:nh": {
        "title": "Natural History",
        "author": "Pliny the Elder",
        "category": ANCIENT,
        "translation": "John Bostock and H. T. Riley (1855)",
        "urls": {
            "book5": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0137%3Abook%3D5",
            "book10": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0137%3Abook%3D10",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "pliny:letters": {
        "title": "Letters",
        "author": "Pliny the Younger",
        "category": ANCIENT,
        "translation": "Betty Radice (Penguin, 1963) / Melmoth-Hutchinson (1746)",
        "urls": {
            "book10": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0139%3Abook%3D10",
        },
        "section_pattern": r"(?:Letter\s+\d+|\b(\d+)\.\s)",
    },

    "plutarch:lives": {
        "title": "Parallel Lives",
        "author": "Plutarch",
        "category": ANCIENT,
        "translation": "Bernadotte Perrin (Loeb, 1914-1926)",
        "urls": {
            "sertorius": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Sertorius*.html",
            "caesar": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Caesar*.html",
            "alexander_1": "https://penelope.uchicago.edu/Thayer/e/roman/texts/plutarch/lives/alexander*/3.html",
            "alexander_2": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Alexander*/4.html",
            "alexander_3": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Alexander*/5.html",
            "alexander_4": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Alexander*/6-7.html",
            "alexander_5": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Alexander*/8.html",
            "pompey": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Plutarch/Lives/Pompey*.html",
        },
        "alt_urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A2008.01.0002",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "cassiusdio:romanhistory": {
        "title": "Roman History",
        "author": "Cassius Dio",
        "category": ANCIENT,
        "translation": "Earnest Cary (Loeb, 1914-1927)",
        "urls": {
            "book51": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/51*.html",
            "book60": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/60*.html",
            "book66": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Cassius_Dio/66*.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "polybius:histories": {
        "title": "Histories",
        "author": "Polybius",
        "category": ANCIENT,
        "translation": "Evelyn S. Shuckburgh (1889)",
        "urls": {
            f"book{i}": f"https://penelope.uchicago.edu/Thayer/e/roman/texts/polybius/{i}*.html"
            for i in range(1, 7)
        },
        "alt_urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0234",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "cicero:philippics": {
        "title": "Philippics",
        "author": "Marcus Tullius Cicero",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1903)",
        "urls": {
            "full": "https://www.attalus.org/cicero/philippic13.html",
        },
        "note": "Downloading Philippic 13 (the cited one). W.C.A. Ker translation (1926).",
        "section_pattern": r"(?:Philippic\s+\d+|\b(\d+)\.\s)",
    },

    "cicero:catilinam": {
        "title": "In Catilinam",
        "author": "Marcus Tullius Cicero",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1903)",
        "urls": {
            "full": "https://www.attalus.org/cicero/catilina2.html",
        },
        "note": "Second Catilinarian Oration (the cited one).",
        "section_pattern": r"\[(\d+)\]",
    },

    "seneca:epistles": {
        "title": "Epistulae Morales ad Lucilium",
        "author": "Lucius Annaeus Seneca",
        "category": ANCIENT,
        "translation": "Richard M. Gummere (Loeb, 1917-1925)",
        "urls": {
            "full": "https://en.wikisource.org/wiki/Moral_letters_to_Lucilius/Letter_101",
        },
        "note": "Downloading Epistle 101 (the cited one). Gummere translation on Wikisource.",
        "section_pattern": r"(?:Letter\s+\d+|Epistle\s+\d+|\b(\d+)\.\s)",
    },

    "xenophon:memorabilia": {
        "title": "Memorabilia",
        "author": "Xenophon",
        "category": ANCIENT,
        "translation": "H. G. Dakyns (1897)",
        "urls": {
            "full": "https://www.gutenberg.org/files/1177/1177-h/1177-h.htm",
        },
        "note": "Project Gutenberg. Dakyns translation. All 4 books on single page.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "xenophon:cyropaedia": {
        "title": "Cyropaedia",
        "author": "Xenophon",
        "category": ANCIENT,
        "translation": "H. G. Dakyns, rev. F. M. Stawell (1897)",
        "urls": {
            "full": "https://www.gutenberg.org/files/2085/2085-h/2085-h.htm",
        },
        "note": "Project Gutenberg. All 8 books on single page.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\.\s)",
    },

    "herodotus:histories": {
        "title": "Histories",
        "author": "Herodotus",
        "category": ANCIENT,
        "translation": "G. C. Macaulay (1890)",
        "urls": {
            "full": "https://www.gutenberg.org/files/2707/2707-h/2707-h.htm",
        },
        "note": "Project Gutenberg. Macaulay translation. All 9 books on single page.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "epictetus:discourses": {
        "title": "Discourses",
        "author": "Epictetus (recorded by Arrian)",
        "category": ANCIENT,
        "translation": "George Long (1877)",
        "urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0236",
        },
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "strabo:geography": {
        "title": "Geography",
        "author": "Strabo",
        "category": ANCIENT,
        "translation": "H. L. Jones (Loeb, 1917-1932)",
        "urls": {
            "book16ch1": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/16A*.html",
            "book16ch2": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/16B*.html",
            "book16ch3": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/16C*.html",
            "book17ch1a": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/17A1*.html",
            "book17ch1b": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Strabo/17A2*.html",
        },
        "note": "Only downloading books 16-17 (Near East, Egypt) as most relevant to manuscript.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "lucian:peregrinus": {
        "title": "The Passing of Peregrinus",
        "author": "Lucian of Samosata",
        "category": ANCIENT,
        "translation": "A. M. Harmon (Loeb, 1936)",
        "urls": {
            "full": "https://www.sacred-texts.com/cla/luc/wl4/wl420.htm",
        },
        "alt_urls": {
            "full": "https://en.wikisource.org/wiki/The_Works_of_Lucian_of_Samosata/The_Death_of_Peregrine",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "quintilian:declamation": {
        "title": "Declamationes Minores",
        "author": "Quintilian (attributed)",
        "category": ANCIENT,
        "translation": "Latin text (Winterbottom edition, 1984)",
        "urls": {
            "full": "https://latin.packhum.org/loc/1002/2/60",
        },
        "note": "PHI Latin Texts. Declamation 274 (Latin). No public domain English translation exists.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    # --- Egyptian Primary Texts ---

    "pyramidtexts": {
        "title": "Pyramid Texts",
        "author": "Ancient Egyptian",
        "category": ANCIENT,
        "translation": "Samuel A. B. Mercer (1952)",
        "urls": {
            "full": "https://archive.org/stream/pyramidtextsmercer/Pyramid%20Texts%20Mercer_djvu.txt",
        },
        "note": "Archive.org DjVu text of Mercer's complete translation. All utterances (1-759).",
        "section_pattern": r"(?:Utterance\s+\d+|\b(\d+)\.\s)",
    },

    "coffintexts": {
        "title": "Coffin Texts",
        "author": "Ancient Egyptian",
        "category": ANCIENT,
        "translation": "R. O. Faulkner (1973-1978)",
        "urls": {
            "vol1": "https://archive.org/stream/TheAncientEgyptianCoffin1/The%20ancient%20Egyptian%20coffin1_djvu.txt",
            "vol3": "https://archive.org/stream/TheAncientEgyptianCoffin1/The_ancient_Egyptian%20coffin%20texts3_djvu.txt",
        },
        "note": "Archive.org DjVu text of Faulkner translation. Vol 1: Spells 1-354, Vol 3: Spells 788-1185. "
                "Spells 80 and 335 in vol1, Spell 1130 in vol3.",
        "section_pattern": r"(?:SPELL\s+\d+|Spell\s+\d+|\b(\d+)\.\s)",
    },

    "bookofthedead": {
        "title": "Book of the Dead",
        "author": "Ancient Egyptian",
        "category": ANCIENT,
        "translation": "P. Le Page Renouf and E. Naville (1904)",
        "urls": {
            "full": "https://www.gutenberg.org/files/69566/69566-h/69566-h.htm",
        },
        "note": "Project Gutenberg. Complete Renouf-Naville translation. Chapters 1-186.",
        "section_pattern": r"(?:Chapter\s+\d+|CHAPTER\s+\d+|Spell\s+\d+|\b(\d+)\.\s)",
    },

    "shabaka:memphite": {
        "title": "Memphite Theology (Shabaka Stone)",
        "author": "Ancient Egyptian",
        "category": ANCIENT,
        "translation": "M. Lichtheim (Ancient Egyptian Literature, vol. 1, 1973)",
        "urls": {
            "full": "https://www.attalus.org/egypt/shabaka_stone.html",
        },
        "note": "BM EA 498. Lichtheim translation on attalus.org. Creation by divine speech (Ptah).",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "hymn:aten": {
        "title": "Great Hymn to the Aten",
        "author": "Ancient Egyptian (attributed to Akhenaten)",
        "category": ANCIENT,
        "translation": "John A. Wilson / Lichtheim",
        "urls": {
            "full": "https://en.wikisource.org/wiki/Great_Hymn_to_Aten",
        },
        "note": "Wikisource. Amarna tomb of Ay, c. 1350 BC.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    # --- Additional Ancient Sources ---

    "livy:aburbe": {
        "title": "Ab Urbe Condita (From the Founding of the City)",
        "author": "Titus Livius (Livy)",
        "category": ANCIENT,
        "translation": "Rev. Canon Roberts (1905)",
        "urls": {
            "full": "https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0026",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "suetonius:caesars": {
        "title": "Lives of the Caesars (De Vita Caesarum)",
        "author": "Gaius Suetonius Tranquillus",
        "category": ANCIENT,
        "translation": "J. C. Rolfe (Loeb, 1914)",
        "urls": {
            "julius": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Julius*.html",
            "augustus": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Suetonius/12Caesars/Augustus*.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "achillestatius:leucippe": {
        "title": "Leucippe and Clitophon",
        "author": "Achilles Tatius",
        "category": ANCIENT,
        "translation": "S. Gaselee (Loeb, 1917)",
        "urls": {
            "full": "https://www.gutenberg.org/files/58476/58476-h/58476-h.htm",
        },
        "note": "Project Gutenberg. Greek novel with burial/resurrection themes.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    # --- Greek Classical Literature ---

    "homer:iliad": {
        "title": "Iliad",
        "author": "Homer",
        "category": ANCIENT,
        "translation": "Samuel Butler (1898)",
        "urls": {
            "full": "https://www.gutenberg.org/files/6150/6150-h/6150-h.htm",
        },
        "note": "Project Gutenberg. Butler prose translation. All 24 books.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\.\s)",
    },

    "homer:odyssey": {
        "title": "Odyssey",
        "author": "Homer",
        "category": ANCIENT,
        "translation": "Samuel Butler (1900)",
        "urls": {
            "full": "https://www.gutenberg.org/files/1727/1727-h/1727-h.htm",
        },
        "note": "Project Gutenberg. Butler prose translation. All 24 books.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\.\s)",
    },

    "aeschylus:prometheus": {
        "title": "Prometheus Bound",
        "author": "Aeschylus",
        "category": ANCIENT,
        "translation": "E. D. A. Morshead (1908)",
        "urls": {
            "full": "http://classics.mit.edu/Aeschylus/prometheus.html",
        },
        "note": "MIT Internet Classics Archive.",
        "section_pattern": r"\b(\d+)\b",
    },

    "aeschylus:persians": {
        "title": "The Persians",
        "author": "Aeschylus",
        "category": ANCIENT,
        "translation": "Robert Potter (1882)",
        "urls": {
            "full": "http://classics.mit.edu/Aeschylus/persians.html",
        },
        "note": "MIT Internet Classics Archive.",
        "section_pattern": r"\b(\d+)\b",
    },

    "euripides:bacchae": {
        "title": "The Bacchae",
        "author": "Euripides",
        "category": ANCIENT,
        "translation": "E. P. Coleridge (1891)",
        "urls": {
            "full": "http://classics.mit.edu/Euripides/bacchan.html",
        },
        "note": "MIT Internet Classics Archive.",
        "section_pattern": r"\b(\d+)\b",
    },

    "plato:apology": {
        "title": "Apology",
        "author": "Plato",
        "category": ANCIENT,
        "translation": "Benjamin Jowett (1871)",
        "urls": {
            "full": "http://classics.mit.edu/Plato/apology.html",
        },
        "note": "MIT Internet Classics Archive.",
        "section_pattern": r"\b(\d+)[a-e]?\b",
    },

    "plato:republic": {
        "title": "Republic",
        "author": "Plato",
        "category": ANCIENT,
        "translation": "Benjamin Jowett (1871)",
        "urls": {
            "full": "https://www.gutenberg.org/files/1497/1497-h/1497-h.htm",
        },
        "note": "Project Gutenberg. Jowett translation. All 10 books. Citation [514a-520a] = Book VII (Cave allegory).",
        "section_pattern": r"\b(\d+)[a-e]?\b",
    },

    "plato:statesman": {
        "title": "Statesman",
        "author": "Plato",
        "category": ANCIENT,
        "translation": "Benjamin Jowett (1871)",
        "urls": {
            "full": "http://classics.mit.edu/Plato/stateman.html",
        },
        "note": "MIT Internet Classics Archive. Note: MIT spells it 'stateman'.",
        "section_pattern": r"\b(\d+)[a-e]?\b",
    },

    "aristotle:poetics": {
        "title": "Poetics",
        "author": "Aristotle",
        "category": ANCIENT,
        "translation": "S. H. Butcher (1895)",
        "urls": {
            "part1": "http://classics.mit.edu/Aristotle/poetics.1.1.html",
            "part2": "http://classics.mit.edu/Aristotle/poetics.2.2.html",
            "part3": "http://classics.mit.edu/Aristotle/poetics.3.3.html",
        },
        "note": "MIT Internet Classics Archive.",
        "section_pattern": r"\b(\d+)[a-b]?\b",
    },

    "aristotle:ethics": {
        "title": "Nicomachean Ethics",
        "author": "Aristotle",
        "category": ANCIENT,
        "translation": "W. D. Ross (1908)",
        "urls": {
            "book1": "http://classics.mit.edu/Aristotle/nicomachaen.1.i.html",
            "book2": "http://classics.mit.edu/Aristotle/nicomachaen.2.ii.html",
            "book3": "http://classics.mit.edu/Aristotle/nicomachaen.3.iii.html",
            "book4": "http://classics.mit.edu/Aristotle/nicomachaen.4.iv.html",
            "book5": "http://classics.mit.edu/Aristotle/nicomachaen.5.v.html",
            "book6": "http://classics.mit.edu/Aristotle/nicomachaen.6.vi.html",
            "book7": "http://classics.mit.edu/Aristotle/nicomachaen.7.vii.html",
            "book8": "http://classics.mit.edu/Aristotle/nicomachaen.8.viii.html",
            "book9": "http://classics.mit.edu/Aristotle/nicomachaen.9.ix.html",
            "book10": "http://classics.mit.edu/Aristotle/nicomachaen.10.x.html",
        },
        "note": "MIT Internet Classics Archive. All 10 books on single page.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\b)",
    },

    "aratus:phaenomena": {
        "title": "Phaenomena",
        "author": "Aratus",
        "category": ANCIENT,
        "translation": "G. R. Mair (Loeb, 1921)",
        "urls": {
            "full": "https://www.attalus.org/old/aratus1.html",
        },
        "note": "Attalus.org. Verse astronomical poem. Line 5 cited in Acts 17:28.",
        "section_pattern": r"\b(\d+)\b",
    },

    "thucydides:peloponnesian": {
        "title": "History of the Peloponnesian War",
        "author": "Thucydides",
        "category": ANCIENT,
        "translation": "Richard Crawley (1874)",
        "urls": {
            "full": "https://www.gutenberg.org/files/7142/7142-h/7142-h.htm",
        },
        "note": "Project Gutenberg. Crawley translation. All 8 books.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    # --- More Greco-Roman ---

    "appian:romanhistory": {
        "title": "Roman History (Civil Wars)",
        "author": "Appian of Alexandria",
        "category": ANCIENT,
        "translation": "Horace White (Loeb, 1912-1913)",
        "urls": {
            "civilwars1": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/1*.html",
            "civilwars2": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/2*.html",
            "civilwars3": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/3*.html",
            "civilwars4": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/4*.html",
            "civilwars5": "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Appian/Civil_Wars/5*.html",
        },
        "note": "LacusCurtius. White translation. Civil Wars books 1-5.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "diogenes:lives": {
        "title": "Lives of Eminent Philosophers",
        "author": "Diogenes Laertius",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1853)",
        "urls": {
            "full": "https://www.gutenberg.org/files/57342/57342-h/57342-h.htm",
        },
        "note": "Project Gutenberg. All 10 books. Citation [7.134-147] = Book VII (Zeno/Stoics).",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philostratus:apollonius": {
        "title": "Life of Apollonius of Tyana",
        "author": "Philostratus",
        "category": ANCIENT,
        "translation": "F. C. Conybeare (Loeb, 1912)",
        "urls": {
            "full": "https://archive.org/stream/PhilostratusLifeOfApolloniusOfTyanaConybeareLoebEnglishBooks18Combined/Philostratus,+Life+of+Apollonius+of+Tyana+(Conybeare+Loeb)+English+books+1-8+combined_djvu.txt",
        },
        "note": "Archive.org DjVu text. Conybeare translation. All 8 books.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    # --- Additional Philo ---

    "philo:legatio": {
        "title": "Legatio ad Gaium (Embassy to Gaius)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book40.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:contempl": {
        "title": "De Vita Contemplativa (On the Contemplative Life)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book34.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:vimoysis": {
        "title": "De Vita Moysis (Life of Moses)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "book1": "https://www.earlyjewishwritings.com/text/philo/book25.html",
            "book2": "https://www.earlyjewishwritings.com/text/philo/book26.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "gospelhebrews": {
        "title": "Gospel of the Hebrews (Fragments)",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "M. R. James, Apocryphal New Testament (1924) / Schneemelcher-Wilson",
        "urls": {
            "full": "https://www.earlychristianwritings.com/text/gospelhebrews-mrjames.html",
        },
        "note": "Fragments preserved in Jerome, Origen, Clement. ECW has James translation.",
        "section_pattern": r"(?:Fragment\s+\d+|\b(\d+)\.\s)",
    },

    # --- Philo of Alexandria (8 works) ---

    "philo:specleg": {
        "title": "De Specialibus Legibus (On the Special Laws)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "book1": "https://www.earlyjewishwritings.com/text/philo/book28.html",
            "book2": "https://www.earlyjewishwritings.com/text/philo/book29.html",
            "book3": "https://www.earlyjewishwritings.com/text/philo/book30.html",
            "book4": "https://www.earlyjewishwritings.com/text/philo/book31.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:flaccum": {
        "title": "In Flaccum (Against Flaccus)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book36.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:opificio": {
        "title": "De Opificio Mundi (On the Creation)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book1.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:somniis": {
        "title": "De Somniis (On Dreams)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "book1": "https://www.earlyjewishwritings.com/text/philo/book22.html",
            "book2": "https://www.earlyjewishwritings.com/text/philo/book23.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:cherubim": {
        "title": "De Cherubim (On the Cherubim)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book5.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:sacrificiis": {
        "title": "De Sacrificiis Abelis et Caini (On the Sacrifices of Abel and Cain)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book6.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:confusione": {
        "title": "De Confusione Linguarum (On the Confusion of Tongues)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book15.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:migratione": {
        "title": "De Migratione Abrahami (On the Migration of Abraham)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book16.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:legall": {
        "title": "Legum Allegoriarum (Allegorical Interpretation of the Laws)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "book1": "https://www.earlyjewishwritings.com/text/philo/book2.html",
            "book2": "https://www.earlyjewishwritings.com/text/philo/book3.html",
            "book3": "https://www.earlyjewishwritings.com/text/philo/book4.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "philo:heres": {
        "title": "Quis Rerum Divinarum Heres Sit (Who Is the Heir of Divine Things?)",
        "author": "Philo of Alexandria",
        "category": ANCIENT,
        "translation": "C. D. Yonge (1854-1890)",
        "urls": {
            "full": "https://www.earlyjewishwritings.com/text/philo/book18.html",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    # =========================================================================
    #  PATRISTIC SOURCES (Church Fathers & Early Christian Literature)
    # =========================================================================

    "clement:firstclement": {
        "title": "First Epistle of Clement to the Corinthians",
        "author": "Clement of Rome",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 1, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/1010.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "irenaeus:advhaer": {
        "title": "Against Heresies (Adversus Haereses)",
        "author": "Irenaeus of Lyons",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 1, 1885)",
        "urls": {
            "book1": "https://www.earlychristianwritings.com/text/irenaeus-book1.html",
            "book2": "https://www.earlychristianwritings.com/text/irenaeus-book2.html",
            "book3": "https://www.earlychristianwritings.com/text/irenaeus-book3.html",
            "book4": "https://www.earlychristianwritings.com/text/irenaeus-book4.html",
            "book5": "https://www.earlychristianwritings.com/text/irenaeus-book5.html",
        },
        "note": "Early Christian Writings. Same Roberts-Donaldson ANF translation. One page per book.",
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "tertullian:resurrection": {
        "title": "On the Resurrection of the Flesh",
        "author": "Tertullian",
        "category": PATRISTIC,
        "translation": "Peter Holmes (ANF Vol. 3, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0316.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "tertullian:marcionem": {
        "title": "Adversus Marcionem (Against Marcion)",
        "author": "Tertullian",
        "category": PATRISTIC,
        "translation": "Peter Holmes (ANF Vol. 3, 1885)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/03121.htm",
            "book2": "https://www.newadvent.org/fathers/03122.htm",
            "book3": "https://www.newadvent.org/fathers/03123.htm",
            "book4": "https://www.newadvent.org/fathers/03124.htm",
            "book5": "https://www.newadvent.org/fathers/03125.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "tertullian:apology": {
        "title": "Apology",
        "author": "Tertullian",
        "category": PATRISTIC,
        "translation": "S. Thelwall (ANF Vol. 3, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0301.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "origen:contracels": {
        "title": "Contra Celsum (Against Celsus)",
        "author": "Origen of Alexandria",
        "category": PATRISTIC,
        "translation": "Frederick Crombie (ANF Vol. 4, 1885)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/04161.htm",
            "book2": "https://www.newadvent.org/fathers/04162.htm",
            "book3": "https://www.newadvent.org/fathers/04163.htm",
            "book4": "https://www.newadvent.org/fathers/04164.htm",
            "book5": "https://www.newadvent.org/fathers/04165.htm",
            "book6": "https://www.newadvent.org/fathers/04166.htm",
            "book7": "https://www.newadvent.org/fathers/04167.htm",
            "book8": "https://www.newadvent.org/fathers/04168.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "origen:principiis": {
        "title": "De Principiis (On First Principles)",
        "author": "Origen of Alexandria",
        "category": PATRISTIC,
        "translation": "Frederick Crombie (ANF Vol. 4, 1885)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/04121.htm",
            "book2": "https://www.newadvent.org/fathers/04122.htm",
            "book3": "https://www.newadvent.org/fathers/04123.htm",
            "book4": "https://www.newadvent.org/fathers/04124.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "eusebius:he": {
        "title": "Ecclesiastical History (Historia Ecclesiastica)",
        "author": "Eusebius of Caesarea",
        "category": PATRISTIC,
        "translation": "Arthur Cushman McGiffert (NPNF Ser. 2, Vol. 1, 1890)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/250101.htm",
            "book2": "https://www.newadvent.org/fathers/250102.htm",
            "book3": "https://www.newadvent.org/fathers/250103.htm",
            "book4": "https://www.newadvent.org/fathers/250104.htm",
            "book5": "https://www.newadvent.org/fathers/250105.htm",
            "book6": "https://www.newadvent.org/fathers/250106.htm",
            "book7": "https://www.newadvent.org/fathers/250107.htm",
            "book8": "https://www.newadvent.org/fathers/250108.htm",
            "book9": "https://www.newadvent.org/fathers/250109.htm",
            "book10": "https://www.newadvent.org/fathers/250110.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "eusebius:vita": {
        "title": "Life of Constantine (Vita Constantini)",
        "author": "Eusebius of Caesarea",
        "category": PATRISTIC,
        "translation": "Arthur Cushman McGiffert / Ernest Cushing Richardson (NPNF Ser. 2, Vol. 1, 1890)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/25021.htm",
            "book2": "https://www.newadvent.org/fathers/25022.htm",
            "book3": "https://www.newadvent.org/fathers/25023.htm",
            "book4": "https://www.newadvent.org/fathers/25024.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "clement:stromata": {
        "title": "Stromata (Miscellanies)",
        "author": "Clement of Alexandria",
        "category": PATRISTIC,
        "translation": "William Wilson (ANF Vol. 2, 1885)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/02101.htm",
            "book2": "https://www.newadvent.org/fathers/02102.htm",
            "book3": "https://www.newadvent.org/fathers/02103.htm",
            "book4": "https://www.newadvent.org/fathers/02104.htm",
            "book5": "https://www.newadvent.org/fathers/02105.htm",
            "book6": "https://www.newadvent.org/fathers/02106.htm",
            "book7": "https://www.newadvent.org/fathers/02107.htm",
            "book8": "https://www.newadvent.org/fathers/02108.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "clement:exhortation": {
        "title": "Exhortation to the Greeks (Protrepticus)",
        "author": "Clement of Alexandria",
        "category": PATRISTIC,
        "translation": "William Wilson (ANF Vol. 2, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0208.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "augustine:civdei": {
        "title": "The City of God (De Civitate Dei)",
        "author": "Augustine of Hippo",
        "category": PATRISTIC,
        "translation": "Marcus Dods (NPNF Ser. 1, Vol. 2, 1887)",
        "urls": {
            f"book{i}": f"https://www.newadvent.org/fathers/1201{i:02d}.htm"
            for i in range(1, 23)
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "augustine:consensu": {
        "title": "De Consensu Evangelistarum (On the Harmony of the Evangelists)",
        "author": "Augustine of Hippo",
        "category": PATRISTIC,
        "translation": "S. D. F. Salmond (NPNF Ser. 1, Vol. 6, 1888)",
        "urls": {
            "index": "https://www.newadvent.org/fathers/1602.htm",
        },
        "note": "New Advent splits this by chapter (e.g. 1602101.htm = Book I Ch. 1). Index page has full TOC.",
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "justinmartyr:apology": {
        "title": "First Apology",
        "author": "Justin Martyr",
        "category": PATRISTIC,
        "translation": "Marcus Dods and George Reith (ANF Vol. 1, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0126.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "justinmartyr:trypho": {
        "title": "Dialogue with Trypho",
        "author": "Justin Martyr",
        "category": PATRISTIC,
        "translation": "Marcus Dods and George Reith (ANF Vol. 1, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/01287.htm",
        },
        "note": "Chapters 89-108 (second part). Mary-Eve typology at Chapter 100.",
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "ignatius:letters": {
        "title": "Letters of Ignatius",
        "author": "Ignatius of Antioch",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 1, 1885)",
        "urls": {
            "ephesians": "https://www.newadvent.org/fathers/0104.htm",
            "magnesians": "https://www.newadvent.org/fathers/0105.htm",
            "trallians": "https://www.newadvent.org/fathers/0106.htm",
            "romans": "https://www.newadvent.org/fathers/0107.htm",
            "philadelphians": "https://www.newadvent.org/fathers/0108.htm",
            "smyrnaeans": "https://www.newadvent.org/fathers/0109.htm",
            "polycarp": "https://www.newadvent.org/fathers/0110.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "polycarp:philippians": {
        "title": "Letter to the Philippians",
        "author": "Polycarp of Smyrna",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 1, 1885)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0136.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "didache": {
        "title": "Didache (Teaching of the Twelve Apostles)",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 7, 1886)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0714.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "shepherd:hermas": {
        "title": "The Shepherd of Hermas",
        "author": "Hermas",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 2, 1885)",
        "urls": {
            "full": "https://www.earlychristianwritings.com/text/shepherd.html",
        },
        "alt_urls": {
            "visions": "https://www.newadvent.org/fathers/02011.htm",
            "mandates": "https://www.newadvent.org/fathers/02012.htm",
            "similitudes": "https://www.newadvent.org/fathers/02013.htm",
        },
        "note": "Full text on earlychristianwritings.com (Visions + Mandates + Similitudes). New Advent has separate pages but rate-limits.",
        "section_pattern": r"(?:Vision\s+\d+|Mandate\s+\d+|Similitude\s+\d+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "protoevangelium": {
        "title": "Protoevangelium of James",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "Roberts-Donaldson (ANF Vol. 8, 1886)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0847.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "epiphanius:panarion": {
        "title": "Panarion (Adversus Haereses)",
        "author": "Epiphanius of Salamis",
        "category": PATRISTIC,
        "translation": "Frank Williams (Brill, 1987/2009)",
        "urls": {
            "full": "https://gnosis.study/library/%D0%9A%D1%80%D0%B8%D1%82%D0%B8%D0%BA%D0%B0/ENG/Epiphanius%20of%20Salamis%20-%20The%20Panarion,%20Book%20I%20(Sects%201-46).pdf",
        },
        "note": "Williams/Brill 2009 2nd edition, Book I (Sects 1-46). Section 42 = Marcion. "
                "PDF from gnosis.study, extracted to text via pymupdf.",
        "section_pattern": r"(?:Heresy\s+\d+|\b(\d+)\.\s)",
    },

    "epiphanius:mensuris": {
        "title": "De Mensuris et Ponderibus (On Weights and Measures)",
        "author": "Epiphanius of Salamis",
        "category": PATRISTIC,
        "translation": "James Elmer Dean (1935)",
        "urls": {
            "full": "https://www.tertullian.org/fathers/epiphanius_weights_03_text.htm",
        },
        "note": "Dean (1935) translation on tertullian.org. Section 14 confirmed present.",
        "section_pattern": r"§\s*(\d+)",
    },

    "lactantius:phoenix": {
        "title": "De Ave Phoenice (The Phoenix)",
        "author": "Lactantius",
        "category": PATRISTIC,
        "translation": "William Fletcher (ANF Vol. 7, 1886)",
        "urls": {
            "latin": "https://www.thelatinlibrary.com/ave.phoen.html",
            "english": "https://www.ewtn.com/catholicism/library/phoenix-de-ave-phoenice-11464",
        },
        "section_pattern": r"\b(\d+)\.\s",
    },

    "lactantius:institutes": {
        "title": "Divinae Institutiones (Divine Institutes)",
        "author": "Lactantius",
        "category": PATRISTIC,
        "translation": "William Fletcher (ANF Vol. 7, 1886)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/07011.htm",
            "book2": "https://www.newadvent.org/fathers/07012.htm",
            "book3": "https://www.newadvent.org/fathers/07013.htm",
            "book4": "https://www.newadvent.org/fathers/07014.htm",
            "book5": "https://www.newadvent.org/fathers/07015.htm",
            "book6": "https://www.newadvent.org/fathers/07016.htm",
            "book7": "https://www.newadvent.org/fathers/07017.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "sulpicius:chronica": {
        "title": "Chronica (Sacred History)",
        "author": "Sulpicius Severus",
        "category": PATRISTIC,
        "translation": "Alexander Roberts (NPNF Ser. 2, Vol. 11, 1894)",
        "urls": {
            "book1": "https://www.newadvent.org/fathers/35051.htm",
            "book2": "https://www.newadvent.org/fathers/35052.htm",
        },
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "victorinus:apocalypse": {
        "title": "Commentary on the Apocalypse",
        "author": "Victorinus of Pettau",
        "category": PATRISTIC,
        "translation": "Robert Ernest Wallis (ANF Vol. 7, 1886)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0712.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "cyprian:lapsed": {
        "title": "De Lapsis (On the Lapsed)",
        "author": "Cyprian of Carthage",
        "category": PATRISTIC,
        "translation": "Robert Ernest Wallis (ANF Vol. 5, 1886)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/050703.htm",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    # --- Additional Patristic & Apocryphal Sources ---

    "barnabas:epistle": {
        "title": "Epistle of Barnabas",
        "author": "Pseudo-Barnabas",
        "category": PATRISTIC,
        "translation": "J. B. Lightfoot (1891)",
        "urls": {
            "full": "https://www.earlychristianwritings.com/text/barnabas-lightfoot.html",
        },
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "socrates:he": {
        "title": "Ecclesiastical History",
        "author": "Socrates Scholasticus",
        "category": PATRISTIC,
        "translation": "A. C. Zenos (NPNF Ser. 2, Vol. 2, 1890)",
        "urls": {
            "full": "https://archive.org/stream/selectlibraryofn02scha/selectlibraryofn02scha_djvu.txt",
        },
        "note": "Archive.org DjVu text of NPNF Ser. 2, Vol. 2. Contains Socrates + Sozomen.",
        "section_pattern": r"(?:Book\s+[IVXLC]+|Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "hippolytus:daniel": {
        "title": "Commentary on Daniel",
        "author": "Hippolytus of Rome",
        "category": PATRISTIC,
        "translation": "S. D. F. Salmond (ANF Vol. 5, 1886)",
        "urls": {
            "full": "https://www.newadvent.org/fathers/0520.htm",
        },
        "note": "ANF has fragments/scholia on Daniel. Full commentary only in T. C. Schmidt (2017, copyrighted).",
        "section_pattern": r"(?:Chapter\s+\d+|\b(\d+)\.\s)",
    },

    "gospelpeter": {
        "title": "Gospel of Peter (Fragment)",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "M. R. James, Apocryphal New Testament (1924)",
        "urls": {
            "full": "https://www.earlychristianwritings.com/text/gospelpeter-mrjames.html",
        },
        "note": "Akhmim fragment. Passion and resurrection narrative.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "actascillitanorum": {
        "title": "Acts of the Scillitan Martyrs",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "J. A. Robinson (1891)",
        "urls": {
            "full": "https://www.earlychristianwritings.com/text/scillitan.html",
        },
        "note": "Earliest dated document of the Latin church (180 AD).",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "fourezdras": {
        "title": "4 Ezra (2 Esdras)",
        "author": "Anonymous",
        "category": PATRISTIC,
        "translation": "KJV Apocrypha / R. H. Charles (1913)",
        "urls": {
            "full": "https://www.pseudepigrapha.com/apocrypha_ot/2esdr.htm",
        },
        "note": "Jewish apocalypse, late 1st century AD. Pseudepigrapha.com.",
        "section_pattern": r"\b(\d+)\.\s",
    },

    "sibyllineoracles": {
        "title": "Sibylline Oracles",
        "author": "Various (Jewish and Christian)",
        "category": PATRISTIC,
        "translation": "Milton S. Terry (1890)",
        "urls": {
            "full": "https://archive.org/stream/sibyllineoracle00terrgoog/sibyllineoracle00terrgoog_djvu.txt",
        },
        "note": "Archive.org DjVu text. Terry verse translation. All 14 books.",
        "section_pattern": r"(?:BOOK\s+[IVXLC]+|\b(\d+)\b)",
    },

    "ezekieldramatist:exagoge": {
        "title": "Exagoge (Exodus drama fragments)",
        "author": "Ezekiel the Tragedian",
        "category": ANCIENT,
        "translation": "E. H. Gifford (1903), via Eusebius Praeparatio Evangelica 9.28-29",
        "urls": {
            "full": "https://www.tertullian.org/fathers/eusebius_pe_09_book9.htm",
        },
        "note": "2nd century BC Jewish-Greek tragedy. Fragments preserved in Eusebius PE 9.28-29. "
                "Gifford 1903 translation (public domain).",
        "section_pattern": r"\b(\d+)\b",
    },

    # --- Patristic sources with no free online translation ---

    "origen:homezek": {
        "title": "Homilies on Ezekiel",
        "author": "Origen of Alexandria",
        "category": PATRISTIC,
        "translation": "Mischa Hooker / Roger Pearse (2014, freely shared)",
        "urls": {
            "full": "https://archive.org/download/OrigenHomiliesOnEzekielEdHooker2014/Origen-Homilies_on_Ezekiel-ed_Hooker-2014_djvu.txt",
        },
        "note": "Hooker/Pearse 2014 edition, 'enjoy, copy, circulate'. Archive.org DjVu text.",
    },

    "origen:homluke": {
        "title": "Homilies on Luke",
        "author": "Origen of Alexandria",
        "category": PATRISTIC,
        "translation": "Joseph T. Lienhard (FC 94, 1996)",
        "urls": {
            "full": "https://archive.org/download/the-fathers-of-the-church-a-new-translation-147-volumes/"
                    "The%20Fathers%20of%20the%20Church%2C%20A%20New%20Translation%2C%20Volume%20094%20"
                    "Homilies%20on%20Luke%20-%20Fragments%20on%20Luke%20-%20Origen_djvu.txt",
        },
        "note": "FC vol. 94. Archive.org community collection DjVu text (freely downloadable).",
    },

    "jerome:matthew": {
        "title": "Commentary on Matthew",
        "author": "Jerome (Hieronymus)",
        "category": PATRISTIC,
        "translation": "Thomas P. Scheck (FC 117, 2008)",
        "urls": {
            "full": "https://archive.org/download/commentary-on-matthew-st-jerome/Commentary%20on%20Matthew%20-%20St%20Jerome_djvu.txt",
        },
        "note": "Archive.org community text upload (freely downloadable). Scheck/CUA Press 2008.",
    },

    "liberpontificalis": {
        "title": "Liber Pontificalis (Book of the Popes)",
        "author": "Various",
        "category": PATRISTIC,
        "translation": "Louise Ropes Loomis (Columbia UP, 1916)",
        "urls": {
            "full": "https://archive.org/stream/bookofpopesliber00loom/bookofpopesliber00loom_djvu.txt",
        },
        "note": "Public domain. Loomis 1916 translation covers through Gregory I (590-604 CE).",
    },

    # =========================================================================
    #  MODERN SCHOLARSHIP — Instructions only (copyrighted)
    # =========================================================================

    "brandon:zealots": {
        "title": "Jesus and the Zealots: A Study of the Political Factor in Primitive Christianity",
        "author": "S. G. F. Brandon",
        "category": MODERN,
        "year": 1967,
        "publisher": "Manchester University Press",
        "obtain": "Library / used bookstores. ISBN 978-0-7190-0325-5. Available on Internet Archive for borrowing.",
    },

    "brandon:fall": {
        "title": "The Fall of Jerusalem and the Christian Church",
        "author": "S. G. F. Brandon",
        "category": MODERN,
        "year": 1951,
        "publisher": "SPCK",
        "obtain": "Library / used bookstores. Available on Internet Archive for borrowing.",
    },

    "tabor:dynasty": {
        "title": "The Jesus Dynasty: The Hidden History of Jesus, His Royal Family, and the Birth of Christianity",
        "author": "James D. Tabor",
        "category": MODERN,
        "year": 2006,
        "publisher": "Simon & Schuster",
        "urls": {
            "full": "https://archive.org/download/the-jesus-dynasty-james-d.-tabor_202301/"
                    "The%20Jesus%20Dynasty%20%28James%20D.%20Tabor%29_djvu.txt",
        },
    },

    "eisenman:james": {
        "title": "James the Brother of Jesus: The Key to Unlocking the Secrets of Early Christianity and the Dead Sea Scrolls",
        "author": "Robert Eisenman",
        "category": MODERN,
        "year": 1997,
        "publisher": "Viking",
        "obtain": "Libraries, used bookstores. ISBN 978-0-14-025773-4. Internet Archive borrowing.",
    },

    "maccoby:revolution": {
        "title": "Revolution in Judea: Jesus and the Jewish Resistance",
        "author": "Hyam Maccoby",
        "category": MODERN,
        "year": 1973,
        "publisher": "Ocean Books",
        "urls": {
            "full": "https://archive.org/download/revolution-in-judaea-jesus-hyam-maccoby/"
                    "Revolution%20in%20Judaea%20-%20Jesus%20%28Hyam%20Maccoby%29_djvu.txt",
        },
    },

    "thiering:jesusman": {
        "title": "Jesus the Man: A New Interpretation from the Dead Sea Scrolls",
        "author": "Barbara Thiering",
        "category": MODERN,
        "year": 1992,
        "publisher": "Doubleday",
        "obtain": "Libraries, used bookstores. ISBN 978-0-385-47375-8.",
    },

    "jacobovici:tomb": {
        "title": "The Jesus Family Tomb: The Discovery, the Investigation, and the Evidence That Could Change History",
        "author": "Simcha Jacobovici and Charles Pellegrino",
        "category": MODERN,
        "year": 2007,
        "publisher": "HarperSanFrancisco",
        "obtain": "Libraries, bookstores. ISBN 978-0-06-119200-2.",
    },

    "baigent:holyblood": {
        "title": "Holy Blood, Holy Grail",
        "author": "Michael Baigent, Richard Leigh, and Henry Lincoln",
        "category": MODERN,
        "year": 1982,
        "publisher": "Jonathan Cape",
        "urls": {
            "full": "https://archive.org/download/HolyBloodholyGrail/HolyBloodholyGrail_djvu.txt",
        },
    },

    "park:ekklesia": {
        "title": "Paul's Ekklesia as a Civic Assembly",
        "author": "Young-Ho Park",
        "category": MODERN,
        "year": 2015,
        "publisher": "Mohr Siebeck",
        "obtain": "Academic libraries. ISBN 978-3-16-153805-3. Mohr Siebeck website.",
    },

    "esler:galatians": {
        "title": "Galatians",
        "author": "Philip F. Esler",
        "category": MODERN,
        "year": 1998,
        "publisher": "Routledge",
        "obtain": "Libraries, bookstores. ISBN 978-0-415-11037-1.",
    },

    "vankooten:ekklesia": {
        "title": "Ἐκκλησία τοῦ θεοῦ: The 'Church of God' and the Civic Assemblies (ἐκκλησίαι) of the Greek Cities in the Roman Empire",
        "author": "George H. van Kooten",
        "category": MODERN,
        "year": 2012,
        "publisher": "New Testament Studies 58(4), pp. 522-548",
        "obtain": "Cambridge Core. DOI: 10.1017/S0028688512000148.",
    },

    "bauckham:eyewitnesses": {
        "title": "Jesus and the Eyewitnesses: The Gospels as Eyewitness Testimony",
        "author": "Richard Bauckham",
        "category": MODERN,
        "year": 2006,
        "publisher": "Eerdmans",
        "obtain": "Widely available. ISBN 978-0-8028-3162-0. Libraries, bookstores, Kindle.",
    },

    "hengel:fourgospels": {
        "title": "The Four Gospels and the One Gospel of Jesus Christ",
        "author": "Martin Hengel",
        "category": MODERN,
        "year": 2000,
        "publisher": "SCM Press",
        "obtain": "Libraries. ISBN 978-0-334-02826-7.",
    },

    "brown:johannine": {
        "title": "The Community of the Beloved Disciple",
        "author": "Raymond E. Brown",
        "category": MODERN,
        "year": 1979,
        "publisher": "Paulist Press",
        "obtain": "Widely available. ISBN 978-0-8091-2174-5. Libraries, bookstores.",
    },

    "hurtado:lordjc": {
        "title": "Lord Jesus Christ: Devotion to Jesus in Earliest Christianity",
        "author": "Larry W. Hurtado",
        "category": MODERN,
        "year": 2003,
        "publisher": "Eerdmans",
        "obtain": "Widely available. ISBN 978-0-8028-6070-5. Libraries, bookstores, Kindle.",
    },

    "johnson:writings": {
        "title": "The Writings of the New Testament: An Interpretation",
        "author": "Luke Timothy Johnson",
        "category": MODERN,
        "year": 1999,
        "publisher": "Fortress Press",
        "obtain": "Libraries, bookstores. ISBN 978-0-8006-3439-9.",
    },

    "meeks:urban": {
        "title": "The First Urban Christians: The Social World of the Apostle Paul",
        "author": "Wayne A. Meeks",
        "category": MODERN,
        "year": 2003,
        "publisher": "Yale University Press",
        "obtain": "Widely available. ISBN 978-0-300-09861-7. Libraries, bookstores.",
    },

    "sanders:jesus": {
        "title": "The Historical Figure of Jesus",
        "author": "E. P. Sanders",
        "category": MODERN,
        "year": 1993,
        "publisher": "Penguin",
        "urls": {
            "full": "https://archive.org/download/historical-figure-of-jesus-e.-p.-sanders/"
                    "Historical%20Figure%20of%20Jesus%20%28E.P.%20Sanders%29_djvu.txt",
        },
    },

    "vermes:jesus": {
        "title": "Jesus the Jew: A Historian's Reading of the Gospels",
        "author": "Geza Vermes",
        "category": MODERN,
        "year": 1973,
        "publisher": "Collins",
        "urls": {
            "full": "https://archive.org/download/jesus-the-jew-geza-vermes_202209/"
                    "Jesus%20the%20Jew%20%28Geza%20Vermes%29_djvu.txt",
        },
    },

    "dodd:fourthgospel": {
        "title": "The Interpretation of the Fourth Gospel",
        "author": "C. H. Dodd",
        "category": MODERN,
        "year": 1953,
        "publisher": "Cambridge University Press",
        "obtain": "Libraries. ISBN 978-0-521-09517-7. Still in print from CUP.",
    },

    "borgen:philo": {
        "title": "Philo, John, and Paul: New Perspectives on Judaism and Early Christianity",
        "author": "Peder Borgen",
        "category": MODERN,
        "year": 1987,
        "publisher": "Scholars Press",
        "obtain": "Academic libraries. Out of print. Internet Archive borrowing.",
    },

    "boyarin:jewishgospels": {
        "title": "The Jewish Gospels: The Story of the Jewish Christ",
        "author": "Daniel Boyarin",
        "category": MODERN,
        "year": 2012,
        "publisher": "The New Press",
        "obtain": "Widely available. ISBN 978-1-59558-878-4. Libraries, bookstores, Kindle.",
    },

    "runia:philo": {
        "title": "Philo in Early Christian Literature",
        "author": "David T. Runia",
        "category": MODERN,
        "year": 1993,
        "publisher": "Van Gorcum",
        "obtain": "Academic libraries. ISBN 978-90-232-2741-1.",
    },

    "schrader:martha": {
        "title": "Was Martha of Bethany Added to the Fourth Gospel in the Second Century?",
        "author": "Elizabeth Schrader Polczer",
        "category": MODERN,
        "year": 2017,
        "publisher": "Harvard Theological Review (article)",
        "urls": {
            "full": "https://waynenorthey.com/wp-content/uploads/2022/08/Schrader-18.May_.2016.pdf",
        },
        "note": "Pre-print PDF. Published version: HTR 110:3 (2017).",
    },

    "deboer:magdalene": {
        "title": "The Gospel of Mary: Beyond a Gnostic and a Biblical Mary Magdalene",
        "author": "Esther A. de Boer",
        "category": MODERN,
        "year": 2004,
        "publisher": "T&T Clark",
        "obtain": "Academic libraries. ISBN 978-0-567-08265-0.",
    },

    "hillar:logos": {
        "title": "From Logos to Trinity: The Evolution of Religious Beliefs from Pythagoras to Tertullian",
        "author": "Marian Hillar",
        "category": MODERN,
        "year": 2012,
        "publisher": "Cambridge University Press",
        "urls": {
            "full": "https://www.bethanyipcmm.org/wp-content/uploads/2020/09/"
                    "Hillar-M-2012-From-Logos-to-Trinity-The-Evolution-from-Pythagoras-to-Tertullian-Cambridge.pdf",
        },
    },

    "attridge:essays": {
        "title": "Essays on John and Hebrews",
        "author": "Harold W. Attridge",
        "category": MODERN,
        "year": 2010,
        "publisher": "Mohr Siebeck",
        "obtain": "Academic libraries. ISBN 978-3-16-150tried-8. Mohr Siebeck website.",
    },

    "nongbri:p52": {
        "title": "The Use and Abuse of P52: Papyrological Pitfalls in the Dating of the Fourth Gospel",
        "author": "Brent Nongbri",
        "category": MODERN,
        "year": 2005,
        "publisher": "Harvard Theological Review 98(1), pp. 23-48",
        "obtain": "JSTOR, Cambridge Core. DOI: 10.1017/S0017816005000842.",
    },

    "assmann:searchgod": {
        "title": "The Search for God in Ancient Egypt",
        "author": "Jan Assmann",
        "category": MODERN,
        "year": 2001,
        "publisher": "Cornell University Press",
        "obtain": "Libraries, bookstores. ISBN 978-0-8014-3786-1.",
    },

    "epigraphicsurvey:luxor": {
        "title": "Reliefs and Inscriptions at Luxor Temple, Volume 1: The Festival Procession of Opet in the Colonnade Hall",
        "author": "Epigraphic Survey (Oriental Institute)",
        "category": MODERN,
        "year": 1994,
        "publisher": "Oriental Institute Publications (OIP 112)",
        "urls": {
            "full": "https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/oip112.pdf",
        },
        "note": "Free PDF from Oriental Institute. OIP 112.",
    },

    "harnack:mission": {
        "title": "The Mission and Expansion of Christianity in the First Three Centuries",
        "author": "Adolf von Harnack",
        "category": MODERN,
        "year": 1908,
        "publisher": "Williams & Norgate (2nd English ed.)",
        "urls": {
            "vol1": "https://archive.org/download/missionexpansion01harn/missionexpansion01harn_djvu.txt",
            "vol2": "https://archive.org/download/missionexpansion02harn/missionexpansion02harn_djvu.txt",
        },
        "note": "Public domain. James Moffatt translation. Archive.org DjVu text.",
    },

    "harnack:marcion": {
        "title": "Marcion: The Gospel of the Alien God",
        "author": "Adolf von Harnack",
        "category": MODERN,
        "year": 1924,
        "publisher": "J. C. Hinrichs (German); English trans. Labyrinth Press, 1990",
        "obtain": "Academic libraries. English translation: John E. Steely and Lyle D. Bierma (1990). ISBN 978-0-939464-16-0.",
    },

    "stark:rise": {
        "title": "The Rise of Christianity: A Sociologist Reconsiders History",
        "author": "Rodney Stark",
        "category": MODERN,
        "year": 1996,
        "publisher": "Princeton University Press",
        "obtain": "Widely available. ISBN 978-0-06-067701-5. Libraries, bookstores.",
    },

    "friesen:imperial": {
        "title": "Imperial Cults and the Apocalypse of John: Reading Revelation in the Ruins",
        "author": "Steven J. Friesen",
        "category": MODERN,
        "year": 2001,
        "publisher": "Oxford University Press",
        "obtain": "Academic libraries. ISBN 978-0-19-513153-4.",
    },

    "harland:associations": {
        "title": "Associations, Synagogues, and Congregations: Claiming a Place in Ancient Mediterranean Society",
        "author": "Philip A. Harland",
        "category": MODERN,
        "year": 2003,
        "publisher": "Fortress Press",
        "obtain": "Academic libraries. ISBN 978-0-8006-3609-6.",
    },

    "pelegbarkat:herodian": {
        "title": "The Temple Mount Excavations in Jerusalem 1968-1978 Directed by Benjamin Mazar. Final Reports, Volume V: Herodian Architectural Decoration and King Herod's Royal Portico",
        "author": "Orit Peleg-Barkat",
        "category": MODERN,
        "year": 2017,
        "publisher": "Israel Exploration Society / Hebrew University",
        "obtain": "Academic libraries. Qedem Monograph 57. Israel Exploration Society.",
    },

    "hirschfeld:ramathanadiv": {
        "title": "Ramat Hanadiv Excavations: Final Report of the 1984-1998 Seasons",
        "author": "Yizhar Hirschfeld",
        "category": MODERN,
        "year": 2000,
        "publisher": "Israel Exploration Society",
        "obtain": "Academic libraries. Published by IES, Jerusalem.",
    },
}


def get_sources_by_category(category):
    """Return all sources matching the given category."""
    return {k: v for k, v in SOURCES.items() if v["category"] == category}


def get_downloadable_sources():
    """Return all sources that have URLs (any category with urls)."""
    return {
        k: v for k, v in SOURCES.items()
        if v.get("urls")
    }


def get_all_keys():
    """Return all bibliography keys."""
    return list(SOURCES.keys())


if __name__ == "__main__":
    import sys

    ancient = get_sources_by_category(ANCIENT)
    patristic = get_sources_by_category(PATRISTIC)
    modern = get_sources_by_category(MODERN)
    downloadable = get_downloadable_sources()

    print(f"Total sources: {len(SOURCES)}")
    print(f"  Ancient:    {len(ancient)}")
    print(f"  Patristic:  {len(patristic)}")
    print(f"  Modern:     {len(modern)}")
    print(f"  Downloadable (have URLs): {len(downloadable)}")

    if "--list" in sys.argv:
        for key, src in SOURCES.items():
            urls = len(src.get("urls", {}))
            status = f"({urls} URLs)" if urls else "(instructions only)"
            print(f"  {key}: {src['title']} {status}")
