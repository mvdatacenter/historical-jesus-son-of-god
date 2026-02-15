# Citation Gaps — Full Audit

Every line where a specific ancient source, scholar, or inscription is mentioned
without a `\cite` command. Organized by chapter, then by priority.

**Priority levels:**
- **A** = Bib entry already exists, just add `\cite` (easy fix)
- **B** = Needs new bib entry + `\cite` (medium effort)
- **C** = Nice-to-have / inline reference may be acceptable
- **X** = CLAUDE.md violation ("many scholars" without names)

---

## Preface

No citation gaps found. Methodological introduction only.

---

## Chapter 1

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L60 | B | "the Egyptian" prophet who led thousands to the Mount of Olives | Josephus, Ant 20.169-172 or War 2.261-263 |
| 2 | L64 | A | Judas the Galilean revolt at census of 6 CE | `\cite[18.1--10]{josephus:ant}` or `\cite[2.117]{josephus:war}` |
| 3 | L81 | A | "Irenaeus, writing in the late second century, describes Marcion's activity" | `\cite[3.11.7]{irenaeus:advhaer}` |
| 4 | L86 | A | "Irenaeus... is notably more reserved when assigning Gospel authorship" | `\cite[3.1.1]{irenaeus:advhaer}` |
| 5 | L96 | B | "Apollonius of Tyana" — healings, life story parallels | Philostratus, Life of Apollonius |
| 6 | L100 | B | "demoniac of Gerasenes and the Legion... Odysseus and Polyphemus" | Homer, Odyssey 9 |
| 7 | L101 | C | "The Lord's Prayer bears uncanny resemblance to the solar hymns to Aten" | Great Hymn to the Aten |
| 8 | L105 | B | "the trial of Socrates" | Plato, Apology |
| 9 | L115 | A | "Josephus is dismissed as interpolated" (Testimonium) | `\cite[18.63--64]{josephus:ant}` |
| 10 | L156 | C | "Honi the Circle Drawer and Hanina ben Dosa" | Mishnah Ta'anit 3:8; BT Berakhot 33a |

---

## Chapter 2

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L37 | B | "Polybius lamented that future generations would ask where mighty Corinth had once stood" | Polybius, Histories 39.2 |
| 2 | L39 | B | "ancient sources report that Sulla crushed a vast coalition" | Appian, Mithridatic Wars; Plutarch, Life of Sulla |
| 3 | L151 | B | "Helena, born around 250 CE and later Augusta" — church construction in Galilee | Eusebius, Vita Constantini 3.41-43 |
| 4 | L182 | A | "Josephus... His extremely extensive book did not mention a city of Nazareth" | `\cite{josephus:war}` or `\cite{josephus:life}` |
| 5 | L208 | B | "Strabo, a contemporary of Jesus" on Gennesaret | Strabo, Geography 16.2.16 |
| 6 | L208 | A | "Josephus, who called it the most beautiful and productive land" | `\cite[3.516--521]{josephus:war}` |
| 7 | L329 | B | "Cicero himself explaining he used commentarii" | Cicero, Brutus or Ad Atticum |
| 8 | L335 | B | "In the preface Xenophon explains that this work is a record of what he remembered" | Xenophon, Memorabilia 1.1 (bib entry `xenophon:memorabilia` exists) |
| 9 | L375 | C | "Oath of Loyalty to King Antiochus III" ending with kingdom/power/glory | Specific inscription reference needed |
| 10 | L402 | B | "Aristophanes and Demosthenes mock 'overdressed youths at the assembly'" | Aristophanes, Ecclesiazusae; Demosthenes, specific oration |
| 11 | L450 | B | "Demosthenes employed parabolai in political speeches" | Demosthenes, specific oration |
| 12 | L481 | B | "a rare usage in Aeschylus (Prometheus Bound)" of christos | Aeschylus, Prometheus Bound |
| 13 | L506 | A | "Josephus says priestly families kept their lines in public archives" | `\cite[1.30--36]{josephus:apion}` (needs bib entry for Contra Apionem) |
| 14 | L518 | A | "Hegesippus and Julius Africanus also refer to family registers" | `\cite[3.19--20]{eusebius:he}` (Hegesippus quoted there) |
| 15 | L645 | B | "Celsus, the second-century... philosopher and sharp critic" | Origen, Contra Celsum (already cited elsewhere but not here) |
| 16 | L677 | A | "Josephus records that Herod executed several of his own relatives" | `\cite[15.232; 16.394]{josephus:ant}` |
| 17 | L793 | A | Testimonium Flavianum (full quote without cite) | `\cite[18.63--64]{josephus:ant}` |
| 18 | L810 | A | "James, the brother of Jesus who was called Christ" | `\cite[20.200]{josephus:ant}` |
| 19 | L1010 | B | "The Didache's command to fast on Wednesday and Friday" | `\cite[8.1]{didache}` (bib entry `didache` exists) |
| 20 | L1011 | B | "Justin and Barnabas place the resurrection at the beginning of Sunday" | Justin Martyr (bib exists); Epistle of Barnabas (needs bib entry) |
| 21 | L1025 | B | "Pliny, Livy, and Suetonius all describe panic reactions" | Pliny NH; Livy Ab Urbe Condita; Suetonius specific Life |
| 22 | L1026 | B | "Philo portrays Pilate as already politically precarious" | Philo, Legatio ad Gaium 299-305 (needs bib entry) |
| 23 | L1110 | B | "according to the gospel of Peter" | Gospel of Peter 6:24 (needs bib entry) |
| 24 | L1152 | X | "Many scholars point out that Arimathea is a place that does not exist" | CLAUDE.md violation: forbidden without naming who |
| 25 | L1162 | X | "many scholars point out that the victim of crucifixion were always left on the cross" | CLAUDE.md violation: forbidden without naming who |
| 26 | L1163 | A | "Philo of Alexandria...described a case" (38 AD Alexandria) | `\cite[83--84]{philo:flaccum}` (bib exists, cite missing here) |
| 27 | L1219 | B | "Plutarch's speeches, Josephus' battlefield monologues, Achilles Tatius" | Specific works; Achilles Tatius, Leucippe and Clitophon needs bib |
| 28 | L1238 | B | "Thucydides, Polybius, Tacitus, and Josephus narrate moments" | Thucydides needs bib; others exist |
| 29 | L1257 | A | "Josephus records precisely such an intervention" (crucified men taken down) | `\cite[75]{josephus:life}` (bib exists, cite missing) |
| 30 | L1297 | A | "Theudas, Judas the Galilean, Athronges surface briefly in Josephus" | `\cite[20.97--98]{josephus:ant}` etc. |

---

## Chapter 3

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L28 | B | "Alexander the Great claimed descent from Zeus-Ammon, his image appeared with horns" | Plutarch, Life of Alexander 27; Arrian, Anabasis 3.3-4 |
| 2 | L37 | A | "John Hyrcanus was remembered as beloved of God" | `\cite[13.299--300]{josephus:ant}` |
| 3 | L38 | A | "Alexander Jannaeus struck coins inscribed 'Jonathan the King'" | `\cite[13.320]{josephus:ant}` |
| 4 | L39 | A | "Josephus describes them with titles such as 'savior' and 'chosen of God'" | `\cite{josephus:ant}` with specific passage |
| 5 | L54 | B | "Philo also describes the Therapeutae near Lake Mareotis" | Philo, De Vita Contemplativa |
| 6 | L70 | A | "Josephus mentions 'James, the brother of Jesus who was called Christ'" | `\cite[20.200]{josephus:ant}` |
| 7 | L93 | B | "he quotes the hymn to Zeus: 'For we are indeed his offspring'" | Aratus, Phaenomena 5; Cleanthes, Hymn to Zeus |
| 8 | L98 | A | "Philo of Alexandria had already developed a theology of the Logos" | `\cite{philo:opificio}` or `\cite{philo:somniis}` |
| 9 | L305 | B | "Greek Magical Papyri from Roman Egypt (PGM IV)" | PGM IV (Betz edition) |
| 10 | L466 | B | "Heraclitus, who first introduced it as a principle" | Heraclitus, Fragment B1/B50 (Diels-Kranz) |
| 11 | L468 | B | "Zeno of Citium and later Chrysippus" | Diogenes Laertius, Lives 7.134-147 |
| 12 | L472 | A | "Philo of Alexandria belonged to the narrow Jewish aristocracy" | `\cite{philo:flaccum}` or `\cite{philo:legatio}` |
| 13 | L473 | A | "His brother Alexander the Alabarch" — family connections | `\cite[18.159; 19.276--277]{josephus:ant}` |
| 14 | L479 | A | "Philo described the Logos as the firstborn son of God" | `\cite[146]{philo:confusione}` |
| 15 | L485 | B | "Epiphanes is a title given to multiple rulers, such as Antiochus IV and Ptolemy V" | Rosetta Stone (OGIS 90); Polybius 26.1 |
| 16 | L501 | C | "Hymn to Amun (Papyrus Leiden I 350)" | Papyrus Leiden I 350 (inline ref may be OK) |
| 17 | L514 | C | "Hammurabi, in the prologue to his law code" | Code of Hammurabi, Prologue |
| 18 | L518 | B | "Plato taught that a true philosopher-king is a good shepherd" | Plato, Statesman (Politicus) 275b-c |
| 19 | L540 | C | "Ptolemy V Epiphanes, famous from the Rosetta Stone" | Rosetta Stone (OGIS 90) |
| 20 | L545 | B | "the cave from Plato's Republic" | Plato, Republic 514a-520a |
| 21 | L549 | B | "Claimed sonship of Zeus-Ammon after visiting the oracle at Siwa" | Plutarch, Life of Alexander 27 |
| 22 | L551 | B | "Arrian and Plutarch testify to Alexander's divine self-understanding" | Arrian, Anabasis; Plutarch, Life of Alexander |
| 23 | L556 | B | "Ptolemy I Soter... initiated the cult of Serapis" | Tacitus, Histories 4.83-84; Plutarch, De Iside 28 |
| 24 | L558 | C | "Ptolemy III Euergetes... (Canopus Decree)" | Canopus Decree (OGIS 56) |
| 25 | L563 | B | "Seleucus I Nicator claimed descent from Apollo, reported by Appian" | Appian, Syriaca 56 |
| 26 | L576 | B | "Mithridates VI Eupator, claimed descent from Dionysus and Alexander" | Appian, Mithridatic Wars; Justin, Epitome 38.7 |
| 27 | L597 | B | "Callimachus, in his Aetia, possibly referenced Berenice's Lock" | Callimachus, Aetia fr. 110 (Pfeiffer) |
| 28 | L599 | B | "Manetho (Egyptian Historian, 3rd Century BC)" | Manetho, Aegyptiaca (fragments in Josephus, Contra Apionem) |
| 29 | L648 | B | "in the third century authors like Hippolytus" | Hippolytus, Commentary on Daniel |
| 30 | L671 | C | "LSJ lists 'kingship, dominion'" | LSJ lexicon (standard reference) |
| 31 | L761 | B | "Aristotle uses it in the Poetics (1453a)" | Aristotle, Poetics 1453a |
| 32 | L772 | A | "Polybius" on political cycles | `\cite{polybius:histories}` |
| 33 | L774 | B | "In Aeschylus's Persians, the defeat of Xerxes" | Aeschylus, Persians |
| 34 | L853 | A | "Polybius, writing after witnessing the Greek collapse" | `\cite{polybius:histories}` |

---

## Chapter 4

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L41 | A | "the oldest mention of Marcion is from Tertullian" | `\cite{tertullian:marcionem}` |
| 2 | L60 | A | "Papias refers to gospels" | `\cite[3.39]{eusebius:he}` (Papias fragments) |
| 3 | L60 | A | "Polycarp plausibly wrote before 140AD" | `\cite{polycarp:philippians}` |
| 4 | L60 | A | "Clement quoting Jesus as in the Gospels" | `\cite{clement:firstclement}` |
| 5 | L63 | A | "Justin Martyr most likely quoting the Gospel of John" | `\cite{justinmartyr:trypho}` |
| 6 | L65 | A | "Tertullian, Irenaeus, and Origen all contain unambiguous references" | `\cite{tertullian:marcionem}`, `\cite{irenaeus:advhaer}`, `\cite{origen:contracels}` |
| 7 | L73 | A | "Eusebius attributes the Book of Revelation to John" | `\cite[3.39]{eusebius:he}` |
| 8 | L142 | A | "As Esther de Boer notes" | `\cite{deboer:magdalene}` |
| 9 | L254 | B | "Sappho's fragments emphasize domestic space" | Sappho, standard fragment edition |
| 10 | L256 | B | "Theocritus' 'Women at the Adonis Festival' (Idyll 15)" | Theocritus, Idylls 15 |
| 11 | L269 | X | "Greek narrative theory (Konstan, Burrus)" | Scholar name-drop without content — CLAUDE.md violation |
| 12 | L313 | X | "Modern scholars like Andre Feuillet" | Scholar name-drop without content |
| 13 | L347 | X | "Scholars like Carla Ricci" | Scholar name-drop without content |
| 14 | L459 | X | "Modern critical work by Eldon Epp, Michael Bird" | Scholar name-drop without content |
| 15 | L682 | A | "the Didache, a very early Christian text, also mentions the Eucharist" | `\cite{didache}` |
| 16 | L689 | A | "Justin Martyr accuses followers of Mithras of copying Christian rites" | `\cite[66]{justinmartyr:apology}` |
| 17 | L725 | A | "critics like Celsus" | `\cite{origen:contracels}` (Celsus known through Origen) |
| 18 | L731 | A | "Irenaeus explicitly testifies to Johannine authorship" | `\cite[3.1.1]{irenaeus:advhaer}` |
| 19 | L731 | A | "Polycarp, active around 90AD, knew John's community" | `\cite{polycarp:philippians}` |
| 20 | L899 | A | "Josephus placed the death of Herod at the lunar eclipse" | `\cite[17.167]{josephus:ant}` |
| 21 | L928 | A | "Josephus also states Archelaus ruled while Herod was still alive" | `\cite[17.229--249]{josephus:ant}` |
| 22 | L1017 | B | "Aristotle's hamartia in tragedy" | Aristotle, Poetics 1453a |
| 23 | L1046 | C | "In Ugaritic texts from Bronze Age Syria, kings performed lustration" | KTU corpus |
| 24 | L1062 | B | "The Gospel of the Hebrews reads 'Today I have begotten you'" | Jerome or Epiphanius (patristic fragments) |
| 25 | L1068 | C | "the same word used in imperial decrees such as the Priene inscription" | Priene inscription (OGIS 458) |
| 26 | L1084 | A | "Herodotus describes doves at Zeus's oracle at Dodona" | `\cite[2.55--57]{herodotus:histories}` |
| 27 | L1086 | B | "Homer and Plato both treat Dodona as a Zeus site" | Homer, Iliad 16.233; Plato (specific work) |
| 28 | L1140 | B | "The Gospel of the Hebrews calls the Holy Spirit Jesus's 'Mother'" | Fragment in Origen or Jerome |
| 29 | L1188 | C | "Pyramid and Coffin Texts, and temple programs at Karnak, Luxor" | Standard Egyptological references |
| 30 | L1200 | C | "Lalitavistara (ch. 24) and the Nidanakatha" | Buddhist texts |
| 31 | L1202 | C | "Vendidad 19 and the Denkard 7" | Zoroastrian texts |
| 32 | L1268 | X | "from Harnack to more recent scholarship" | Scholar name-drop without content |
| 33 | L1305 | A | "historians like Herodotus and Thucydides" | `\cite{herodotus:histories}`; Thucydides needs bib |
| 34 | L1324 | A | "Like Polybius, who uses the actions of local leaders" | `\cite{polybius:histories}` |

---

## Chapter 5

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L207 | B | "Aristophanes, Demosthenes, Athenian scholia" on overdressed youths | Aristophanes, Ecclesiazusae; Demosthenes specific oration |
| 2 | L264 | A | "1 Clement, Ignatius, Didache, Shepherd of Hermas, Polycarp" catalog | `\cite{clement:firstclement}`, `\cite{ignatius:letters}`, `\cite{didache}`, `\cite{shepherd:hermas}`, `\cite{polycarp:philippians}` |
| 3 | L264 | B | "Papias, Quadratus, Aristides, Hegesippus" in same catalog | Need bib entries for all four |
| 4 | L445 | B | "Socrates Scholasticus reports cross-like signs at the Serapeum in 391" | Socrates Scholasticus, HE 5.17 |
| 5 | L458 | A | "The Tacitus passage contains the variant 'Chrestianos'" | `\cite[15.44]{tacitus:annals}` |
| 6 | L459 | A | "Pliny the Younger, in his letter to Trajan" | `\cite[10.96]{pliny:letters}` |
| 7 | L482 | B | "the Acta Scillitanorum" | Acta Scillitanorum (needs bib entry) |
| 8 | L533 | A | "comparison with authors such as Polybius" | `\cite{polybius:histories}` |
| 9 | L614 | A | "Eisenman, Sanders, Vermes" (Judaic Sect Model) | Bib entries exist; should `\cite` or remove name-drop |
| 10 | L646 | A | "Clement of Alexandria and Origen repeat these attributions" | `\cite{clement:stromata}`, `\cite{origen:contracels}` |
| 11 | L804 | B | "Origen, in his homilies on Ezekiel and Luke" | Origen, Hom. in Ezech.; Hom. in Luc. |
| 12 | L811 | B | "Jerome, in his prefaces and commentary on Matthew" | Jerome, Comm. in Matt. |
| 13 | L839 | C | "SC 130-133, 379, 505-525" (Seleucid Coins catalog) | Houghton & Lorber, Seleucid Coins |
| 14 | L919 | A | "Philo's De Opificio Mundi 6-25" | `\cite[6--25]{philo:opificio}` |
| 15 | L928 | C | "Opet Festival reliefs at Luxor Temple (OIP 112)" | OIP 112 |
| 16 | L954 | C | "Memphite Theology on the Shabaka Stone" | Lichtheim, Ancient Egyptian Literature vol. 1 |
| 17 | L957 | C | "Coffin Texts, Spell 80, Spell 335, Spell 1130" | de Buck / Faulkner, Coffin Texts |
| 18 | L963 | C | "Book of the Dead Spell 17; Pyramid Texts Utterance 302, 306" | Faulkner editions |
| 19 | L1037 | A | "Josephus records that James was tried and executed (Ant. 20.200-203)" | `\cite[20.200--203]{josephus:ant}` |
| 20 | L1069 | B | "the same structural pattern used by Herodotus, Thucydides, Polybius" | Thucydides needs bib; `\cite{herodotus:histories}`, `\cite{polybius:histories}` |
| 21 | L1073 | A | "Plutarch uses the same narrative grammar for Alexander and Romulus" | `\cite{plutarch:lives}` |
| 22 | L1078 | B | "Bacchae 434-518, Dionysus is arrested, bound, mocked" | Euripides, Bacchae |
| 23 | L1150 | B | "Aristotle defines dikaiosyne as correct placement" | Aristotle, Nicomachean Ethics 5 |
| 24 | L1155 | A | "Polybius treats pistis as the foundation of political order" | `\cite{polybius:histories}` |
| 25 | L1249 | A | "Polybius 5.87.4" | `\cite[5.87.4]{polybius:histories}` |
| 26 | L1349 | A | "R. Bauckham on eyewitness foundations" | `\cite{bauckham:eyewitnesses}` |
| 27 | L1350 | A | "M. Hengel on the early fixed fourfold gospel" | `\cite{hengel:fourgospels}` |
| 28 | L1351 | A | "R. E. Brown on the Johannine community" | `\cite{brown:johannine}` |
| 29 | L1352 | A | "L. T. Johnson and J. M. G. Barclay" | `\cite{johnson:writings,barclay:mediterranean}` |
| 30 | L1353 | A | "L. W. Hurtado on early royal/devotional Christology" | `\cite{hurtado:lordjc}` |

---

## Chapter 6

| # | Line | Priority | Claim | Suggested Source |
|---|------|----------|-------|-----------------|
| 1 | L38 | C | "Roman imperial coinage from the Julio-Claudian period" (phoenix coins) | RIC numismatic volumes |
| 2 | L47 | A | "the Bennu, the solar bird of Ra, venerated at Heliopolis" | `\cite[2.73]{herodotus:histories}` |
| 3 | L58 | B | "Ezekiel the Tragedian describes its breast as porphyrous" | Ezekiel the Tragedian, Exagoge (in Eusebius, PE 9.29) |
| 4 | L60 | B | "'the purple of blood' (to porphyroun haima)" in martyr literature | Specific martyrdom text source needed |
| 5 | L67 | B | "Liber Pontificalis tradition and notes of Giacomo Grimaldi" | Liber Pontificalis; Grimaldi, Descrizione |
| 6 | L127 | B | "Philo presents Moses as the archetypal philosopher" | Philo, De Vita Mosis |
| 7 | L147 | B | "dedications to Theos Hypsistos from the Hellenistic period" | Epigraphic corpus; Mitchell (1999) |
| 8 | L180 | A | "Dio Cassius" for Asia Minor uprisings (Tacitus cited, Dio not) | `\cite{cassiusdio:romanhistory}` |
| 9 | L201 | A | "Josephus, in his Testimonium Flavianum" | `\cite[18.63--64]{josephus:ant}` |
| 10 | L396 | A | "treated as Scripture by Irenaeus, Tertullian, Origen, Clement" (Hermas) | `\cite{irenaeus:advhaer}`, `\cite{clement:stromata}`, `\cite{origen:principiis}` |
| 11 | L410 | B | "Plato hides civic blueprints under the language of the soul" | Plato, Republic |
| 12 | L412 | B | "4 Ezra hides anti-Roman prophecy" | 4 Ezra (2 Esdras) |
| 13 | L413 | B | "The Sibyllines hide insurgent ideology" | Sibylline Oracles |
| 14 | L464 | A | Clement, Exhortation to the Greeks section (no cite) | `\cite{clement:exhortation}` |
| 15 | L470 | A | Cyprian, The Lapsed section (no cite) | `\cite{cyprian:lapsed}` |

---

## Summary Statistics

| Priority | Count | Description |
|----------|-------|-------------|
| **A** | ~65 | Bib entry exists, just add `\cite` |
| **B** | ~55 | Needs new bib entry + `\cite` |
| **C** | ~20 | Nice-to-have, inline may be OK |
| **X** | ~7 | CLAUDE.md violations (unnamed scholars) |
| **TOTAL** | ~147 | |

## New Bib Entries Needed (Priority B sources without bib entries)

### Ancient / Classical
- Apollonius: Philostratus, *Life of Apollonius*
- Homer, *Odyssey*
- Homer, *Iliad*
- Plato, *Apology*
- Plato, *Republic*
- Plato, *Statesman*
- Aristotle, *Poetics*
- Aristotle, *Nicomachean Ethics*
- Aristotle, *Politics*
- Aeschylus, *Persians*
- Aeschylus, *Prometheus Bound*
- Euripides, *Bacchae*
- Aratus, *Phaenomena*
- Callimachus, *Aetia*
- Thucydides, *History of the Peloponnesian War*
- Strabo, *Geography*
- Appian, *Syriaca* / *Mithridatic Wars*
- Diogenes Laertius, *Lives*
- Sappho (fragment edition)
- Theocritus, *Idylls*
- Manetho, *Aegyptiaca*
- Josephus, *Contra Apionem*
- Philo, *De Vita Contemplativa*
- Philo, *De Vita Mosis*
- Philo, *Legatio ad Gaium*

### Patristic / Early Christian
- Epistle of Barnabas
- Gospel of Peter
- Gospel of the Hebrews (fragments)
- Hippolytus, *Commentary on Daniel*
- Socrates Scholasticus, *Historia Ecclesiastica*
- Jerome, *Commentary on Matthew*
- Origen, *Homilies on Ezekiel* / *Homilies on Luke*
- 4 Ezra (2 Esdras)
- Sibylline Oracles
- Acta Scillitanorum
- Liber Pontificalis
- Ezekiel the Tragedian, *Exagoge*

### Modern Scholars (name-dropped without content — fix or cite)
- Harnack, *Mission and Expansion of Christianity*
- Stark, *Rise of Christianity*
- Friesen, *Imperial Cults and the Apocalypse of John*
- Harland, *Associations, Synagogues, and Congregations*
- Rahmani, *Catalogue of Jewish Ossuaries*
- Peleg-Barkat (Herodian architecture)
- Hirschfeld (Ramat HaNadiv excavations)
- Feuillet (John 20 / Song of Songs)
- Ricci (Mary Magdalene)
- Konstan / Burrus (narrative theory)
- Epp / Bird (Junia masculinization)
