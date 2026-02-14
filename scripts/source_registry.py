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
            "full": "https://archive.org/stream/PanarionEpiphaniusCOMPLETE_201905/Panarion%20Epiphanius%20COMPLETE_djvu.txt",
        },
        "note": "Full English translation from Archive.org DjVu text. Brill edition is copyrighted but this OCR text is available.",
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
        "obtain": "Widely available. ISBN 978-0-7432-8723-4. Libraries, bookstores, Kindle.",
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
        "obtain": "Used bookstores. Out of print. Internet Archive borrowing.",
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
        "obtain": "Widely available. ISBN 978-0-09-968241-8. Libraries, bookstores, Kindle.",
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

    "vankooten:cosmic": {
        "title": "Cosmic Christology in Paul and the Pauline School",
        "author": "George H. van Kooten",
        "category": MODERN,
        "year": 2003,
        "publisher": "Mohr Siebeck",
        "obtain": "Academic libraries. ISBN 978-3-16-148169-4. Mohr Siebeck website.",
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

    "barclay:mediterranean": {
        "title": "Paul and the Gift",
        "author": "John M. G. Barclay",
        "category": MODERN,
        "year": 2015,
        "publisher": "Eerdmans",
        "obtain": "Libraries, bookstores. ISBN 978-0-8028-6889-3.",
    },

    "sanders:jesus": {
        "title": "The Historical Figure of Jesus",
        "author": "E. P. Sanders",
        "category": MODERN,
        "year": 1993,
        "publisher": "Penguin",
        "obtain": "Widely available. ISBN 978-0-14-014499-4. Libraries, bookstores, Kindle.",
    },

    "vermes:jesus": {
        "title": "Jesus the Jew: A Historian's Reading of the Gospels",
        "author": "Geza Vermes",
        "category": MODERN,
        "year": 1973,
        "publisher": "Collins",
        "obtain": "Libraries, used bookstores. ISBN 978-0-8006-1443-8.",
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
        "obtain": "JSTOR, Cambridge Core, or Harvard Theological Review website.",
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
        "obtain": "Libraries. ISBN 978-1-107-01330-1. CUP website.",
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
}


def get_sources_by_category(category):
    """Return all sources matching the given category."""
    return {k: v for k, v in SOURCES.items() if v["category"] == category}


def get_downloadable_sources():
    """Return all sources that have URLs (ancient + patristic with urls)."""
    return {
        k: v for k, v in SOURCES.items()
        if v["category"] in (ANCIENT, PATRISTIC) and v.get("urls")
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
