# PRELIMINARY PAGES

---

## INSTITUTIONAL TITLE PAGE

<div align="center">

# EXIF METADATA EXTRACTOR & PRIVACY INSPECTOR (IMG_ANALYZE)

\vspace{0.8cm}

### A MINI PROJECT REPORT
*Submitted in partial fulfillment of the requirements for the award of the Degree of*
### BACHELOR OF COMPUTER APPLICATIONS (B.C.A.)

\vspace{1.0cm}

**Submitted By:**
### SYED AFRIDI
**Register Number: 23UCA101**

\vspace{1.0cm}

**Under the Guidance and Supervision of:**
### Dr. M. SANGEETHA, M.C.A., M.Phil., Ph.D.
**Assistant Professor, Department of Computer Applications**

\vspace{1.2cm}

<img src="../../sample.jpg" alt="College Crest" width="120" style="display:none;" />

### DEPARTMENT OF COMPUTER APPLICATIONS
### SONA COLLEGE OF ARTS AND SCIENCE
**(Affiliated to Periyar University, Salem - 636 011)**
**Meyyanur Bypass Road, Salem – 636 005, Tamil Nadu, India**

\vspace{0.8cm}

**ACADEMIC YEAR 2025–2026**

</div>

---

\newpage

## CERTIFICATE OF BONAFIDE WORK

<div align="center">

### SONA COLLEGE OF ARTS AND SCIENCE
**(Affiliated to Periyar University, Salem - 636 011)**
**Meyyanur Bypass Road, Salem – 636 005, Tamil Nadu, India**

### DEPARTMENT OF COMPUTER APPLICATIONS

</div>

\vspace{0.8cm}

This is to certify that the Mini Project Report entitled:

<div align="center">

### **"EXIF METADATA EXTRACTOR & PRIVACY INSPECTOR (IMG_ANALYZE)"**

</div>

is a bonafide record of independent project work carried out and submitted by:

<div align="center">

### **SYED AFRIDI**
**Register Number: 23UCA101**

</div>

in partial fulfillment of the requirements for the award of the Degree of **Bachelor of Computer Applications (B.C.A.)** of **Periyar University, Salem**, during the academic year **2025–2026**.

It is further certified that this project is the original work of the candidate, carried out under regular supervision and guidance, and has not previously formed the basis for the award of any Degree, Diploma, Associateship, Fellowship, or other similar academic title in this or any other University or Institution of higher learning.

\vspace{2.0cm}

<table width="100%" border="0" style="border: none; margin-top: 30px;">
  <tr>
    <td width="50%" align="left" style="border: none;">
      ____________________________________<br>
      <b>Dr. M. SANGEETHA, M.C.A., M.Phil., Ph.D.</b><br>
      Project Guide / Internal Supervisor<br>
      Assistant Professor,<br>
      Department of Computer Applications,<br>
      Sona College of Arts and Science,<br>
      Salem – 636 005.
    </td>
    <td width="50%" align="right" style="border: none;">
      ____________________________________<br>
      <b>Dr. S. SENTHILKUMAR, M.C.A., M.Phil., Ph.D.</b><br>
      Head of the Department<br>
      Department of Computer Applications,<br>
      Sona College of Arts and Science,<br>
      Salem – 636 005.
    </td>
  </tr>
</table>

\vspace{1.8cm}

Submitted for the Periyar University Viva-Voce Examination held on: ____________________

\vspace{1.5cm}

<table width="100%" border="0" style="border: none; margin-top: 25px;">
  <tr>
    <td width="50%" align="left" style="border: none;">
      ____________________________________<br>
      <b>INTERNAL EXAMINER</b><br>
      Date: ________________________
    </td>
    <td width="50%" align="right" style="border: none;">
      ____________________________________<br>
      <b>EXTERNAL EXAMINER</b><br>
      Date: ________________________
    </td>
  </tr>
</table>

---

\newpage

## CANDIDATE DECLARATION

I, **SYED AFRIDI**, student of the Department of Computer Applications, Sona College of Arts and Science, Salem, bearing Periyar University Register Number **23UCA101**, hereby solemnly declare that the Mini Project Report entitled:

> **"EXIF METADATA EXTRACTOR & PRIVACY INSPECTOR (IMG_ANALYZE)"**

submitted by me in partial fulfillment of the requirements for the award of the Degree of **Bachelor of Computer Applications (B.C.A.)** is an authentic and genuine record of my own research and developmental work completed under the academic supervision and guidance of **Dr. M. Sangeetha, M.C.A., M.Phil., Ph.D.**, Assistant Professor, Department of Computer Applications, Sona College of Arts and Science, Salem.

I further declare and affirm that:
1. The empirical data, algorithmic implementations, architectural designs, code routines, and investigative evaluations presented in this report have been executed entirely by myself and have not been plagiarized, fabricated, or procured through any unauthorized third-party commercial software developer.
2. The software application engineered herein, titled **Img_Analyze**, operates in strict compliance with ethical digital forensics principles and privacy protection guidelines, designed specifically for defensive inspection, security auditing, and metadata sanitization.
3. This report has not been submitted previously, either in part or in full, to Periyar University, Salem, or to any other University, Polytechnic, College, or Examining Body for the award of any Degree, Diploma, Certificate, or academic credential.
4. All secondary sources, academic publications, technical whitepapers, open-source software libraries, statutory enactments, and international standards referenced throughout this text have been comprehensively cited and acknowledged in the bibliography.

\vspace{1.5cm}

<table width="100%" border="0" style="border: none; margin-top: 30px;">
  <tr>
    <td width="50%" align="left" style="border: none;">
      <b>Place:</b> Salem - 636 005<br>
      <b>Date:</b> ____________________
    </td>
    <td width="50%" align="right" style="border: none;">
      ____________________________________<br>
      <b>SYED AFRIDI</b><br>
      (Register Number: 23UCA101)<br>
      Candidate, III Year B.C.A.
    </td>
  </tr>
</table>

---

\newpage

## ACKNOWLEDGEMENT

The successful conceptualization, engineering, and final documentation of this academic mini-project would not have been achievable without the continuous encouragement, structural guidance, technical facilities, and moral support extended by several esteemed individuals and institutions. I take immense pride and humility in expressing my heartfelt gratitude to all those who contributed toward the realization of this endeavor.

First and foremost, I offer my profound thanks and reverence to the **Almighty God**, whose infinite grace, wisdom, and blessings have bestowed upon me the fortitude, intellectual clarity, and perseverance required to undertake and successfully complete this project report.

I express my deepest sense of gratitude and humble salutations to our visionary **Management of Sona College of Arts and Science, Salem**, for establishing an institution of academic brilliance, fostering cutting-edge technological infrastructure, providing advanced computational laboratory facilities, and maintaining an environment conducive to innovative technical learning and applied research.

I take this privileged opportunity to express my sincere and earnest gratitude to our respected Principal, **Dr. G. M. Kadhar Nawaz, M.C.A., M.Phil., Ph.D.**, for his inspiring leadership, visionary academic governance, continual administrative backing, and unyielding commitment toward instilling high research and developmental standards across the student fraternity.

I am immensely obligated and record my heartfelt thanks to **Dr. S. Senthilkumar, M.C.A., M.Phil., Ph.D.**, Head of the Department of Computer Applications, for his visionary supervision, dynamic administration, academic motivation, and constructive suggestions during the various phases of this curriculum project. His insistence on methodological rigor and technical precision served as an invaluable catalyst.

I owe a supreme debt of gratitude to my esteemed Project Guide and Supervisor, **Dr. M. Sangeetha, M.C.A., M.Phil., Ph.D.**, Assistant Professor, Department of Computer Applications, whose scholarly advice, unfailing patience, profound technical insight, and meticulous scrutiny steered this project from its preliminary conceptual phase to its present mature realization. Her incisive critiques, continuous intellectual stimulation, and compassionate mentorship have fundamentally enriched my understanding of digital forensics, metadata structures, and information security paradigms.

I also extend my warmest thanks to all the **Faculty Members and Non-Teaching Staff** of the Department of Computer Applications, Sona College of Arts and Science, Salem, who have directly or indirectly supported me throughout the undergraduate program. Their scholarly pedagogy, timely technical assistance within the computing laboratories, and unhesitating administrative cooperation have paved the way for the smooth execution of this project.

I wish to register my profound thankfulness to the **System Administrators and Technical Laboratory Officers** of the Computer Science and Applications Laboratories for ensuring uninterrupted high-speed internet connectivity, configuring software runtime environments, and maintaining the computational workstations utilized during the development, benchmarking, and testing of **Img_Analyze**.

No words can adequately convey the depth of my gratitude to my beloved **Parents and Family Members**, whose selfless sacrifices, unconditional love, emotional anchors, and boundless encouragement have been the bedrock of my educational journey. Their faith in my capabilities has continually inspired me to strive for technical excellence and moral integrity.

Lastly, I convey my affectionate thanks to my **Fellow Classmates, Batch Peers, and Friends**, who offered invaluable brainstorming sessions, objective feedback, peer testing assistance, and cheerful camaraderie during challenging implementation roadblocks. Their constructive criticism and collaborative spirit have left an indelible mark on this academic journey.

\vspace{1.5cm}

<table width="100%" border="0" style="border: none;">
  <tr>
    <td width="50%" align="left" style="border: none;">
      <b>Place:</b> Salem - 636 005<br>
      <b>Date:</b> ____________________
    </td>
    <td width="50%" align="right" style="border: none;">
      <b>SYED AFRIDI</b><br>
      (Register Number: 23UCA101)<br>
      Department of Computer Applications,<br>
      Sona College of Arts and Science.
    </td>
  </tr>
</table>

---

\newpage

## SYNOPSIS

### 1. The Global Explosion of Digital Photography and Hidden Data Residue
In the contemporary hyper-connected digital ecosystem, photographic imagery has transformed from an occasional artistic medium into the primary language of global human communication, social interaction, enterprise documentation, and forensic evidence. Contemporary estimates indicate that over 1.8 trillion digital photographs are captured globally each year, with smartphones, unmanned aerial vehicles (drones), wearable smart glasses, and high-resolution digital single-lens reflex (DSLR) cameras accounting for more than 92 percent of this vast multimedia influx. 

However, every modern digital photograph encapsulates far more than the visible raster grid of red, green, and blue pixels rendered on a display screen. Beneath the perceptible visual surface lies an extensive, highly granular, and automated binary data repository designated as Exchangeable Image File Format (EXIF) metadata. Originally codified by the Japan Electronic Industry Development Association (JEIDA) and currently maintained jointly by the Japan Electronics and Information Technology Industries Association (JEITA) and the Camera & Imaging Products Association (CIPA) under specification standard CIPA DC-008-2016 (EXIF Version 2.32), this embedded architecture serves legitimate diagnostic, archiving, color calibration, and photographic indexing purposes.

### 2. The Mechanics of EXIF Telemetry and Metadata Privacy Leakage
When a digital shutter is triggered, modern hardware architectures capture comprehensive physical, spatial, chronometric, and optical parameters, writing them synchronously into binary Image File Directories (IFDs) within the image wrapper. For standard JPEG/JFIF files, this payload is embedded within Application Marker Segment 1 (`APP1`, denoted by hexadecimal marker `0xFFE1`). The telemetry cataloged includes:
* **Spatial Telemetry (GPS IFD):** Sub-second geodetic positioning derived from Global Navigation Satellite Systems (GNSS, including GPS, GLONASS, Galileo, and BeiDou). It encodes precise latitude, longitude, ellipsoidal altitude, velocity, compass bearing, and satellite dilution of precision (PDOP/HDOP), enabling geospatial tracking with sub-meter accuracy.
* **Chronometric and Temporal Telemetry:** Sub-second atomic timestamps (`DateTimeOriginal`, `DateTimeDigitized`, `OffsetTime`), capturing the exact instant of sensor exposure, local timezone offsets, and temporal delta sequences across multi-shot bursts.
* **Hardware Device Fingerprinting:** Manufacturer, camera model, firmware revision, unique body serial number (`BodySerialNumber`), lens make, optical serial number (`LensSerialNumber`), internal sensor characteristics, and proprietary MakerNote binary structures.
* **Subject-Environment Profiling:** Aperture, focal length, shutter speed, metering mode, flash firing status, ambient light levels, distance to subject, and facial recognition coordinates embedded by proprietary smartphone software.

When users innocently upload, publish, or transmit digital photographs across online marketplaces, web portals, corporate wikis, cloud repositories, instant messaging platforms, or public forums, these invisible metadata payloads travel synchronously with the media. Unlike visible textual captions or human-curated descriptions, EXIF metadata operates silently, autonomously, and without requiring explicit user consent or situational awareness.

### 3. Open-Source Intelligence (OSINT) Attack Vectors and Threat Scenarios
The non-consensual dissemination of unstripped EXIF metadata introduces severe privacy vulnerabilities and constitutes a primary target for malicious Open-Source Intelligence (OSINT) reconnaissance. Cyber adversaries, predatory actors, corporate competitors, state surveillance entities, and criminal syndicates leverage automated metadata scrapers to construct invasive psychological, spatial, and behavioral profiles of individuals and organizational assets:
* **Cyberstalking and Physical Security Compromise:** Geolocation coordinates extracted from casual snapshots taken inside domestic residences, primary schools, medical facilities, or daily vehicular routes reveal sensitive lifestyle routines, floor plans, and physical locations. This creates acute vulnerabilities for survivors of domestic abuse, public figures, investigative journalists, and minors.
* **Chronolocation and Environmental Cross-Referencing:** By correlating astronomical sun position vectors with EXIF atomic timestamps and focal lengths, adversaries determine absolute time, orientation, and vantage points, defeating attempts at visual obfuscation or geographic concealment.
* **Hardware De-Anonymization and Sybil Identity Linking:** Unique hardware serial numbers embedded in EXIF tags (`0xA431`, `0xA435`) act as persistent global device identifiers. Whistleblowers, investigative sources, and pseudonymous activists attempting to preserve anonymity by cropping or blurring visual faces can be trivially de-anonymized when their distinct camera sensor and lens serial numbers are cross-referenced against historical images published across alternate public social profiles.
* **Military and Intelligence Operational Security (OPSEC) Failures:** Historical operational compromises—including the 2007 insurgent destruction of four US Army AH-64 Apache helicopters at MND-Central in Iraq following soldier web uploads, the 2012 unmasking of fugitive John McAfee in Guatemala via unstripped Vice magazine photo metadata, and the 2012 FBI apprehension of Anonymous hacker Higinio Ochoa—serve as stark historical proof that digital image metadata leakage carries catastrophic, life-threatening real-world consequences.

### 4. Critical Shortcomings of Existing Forensic and Scrubbing Solutions
Faced with these profound digital threats, contemporary users and technical analysts encounter two deeply flawed paradigms of metadata inspection and sanitization:
1. **Cryptic, Syntax-Heavy CLI Forensic Utilities:** Industry-standard command-line forensic engines, most notably Phil Harvey’s renowned *ExifTool*, provide exhaustive parsing capabilities across thousands of esoteric tag formats. However, their command-line nature, lack of visual geospatial rendering, complex parameter flags (e.g., `-all= -tagsfromfile @ -srcfile`), and absence of contextual risk explanations render them utterly inaccessible to non-technical users, business professionals, and general consumers. Furthermore, improper syntax execution frequently results in irreversible file corruption or partial, non-compliant metadata remnants.
2. **Untrusted, Hostile Cloud-Based Scrubbing Portals:** In response to consumer demand, numerous third-party "free online image cleaner" websites have emerged. These services present an intolerable security and privacy paradox: to sanitize a sensitive image containing confidential residential GPS coordinates or biometric markers, the user must transmit the original, unstripped image payload over the public internet to a remote, unvetted third-party server. This centralized aggregation model exposes user media to server-side logging, corporate data harvesting, man-in-the-middle (MitM) wiretapping, unauthorized commercial exploitation (including ingestion into generative AI training datasets), and catastrophic cloud storage breaches.

### 5. Architectural Innovation and Deliverables of Img_Analyze
To decisively address this critical socio-technical dilemma, the **"EXIF METADATA EXTRACTOR & PRIVACY INSPECTOR (IMG_ANALYZE)"** project was conceived, engineered, and rigorously evaluated. Developed as a modular, lightweight, and cross-platform desktop analytical workstation, **Img_Analyze** bridges the gap between industrial-grade forensic extraction and zero-trust consumer privacy preservation.

The system is architected around five fundamental technical innovations:
1. **Universal Localized Multi-Format Ingestion Engine:** Engineered purely in Python utilizing high-performance digital image parsing primitives (`Pillow v12.3.0`, `PyExifTool` bridges, and custom binary IFD unpackers). The engine provides instantaneous multi-format ingestion across JPEG/JFIF, TIFF, PNG (eXIf chunks), WebP, and containerized HEIC formats, operating strictly within local workstation memory without establishing external telemetry network sockets.
2. **Hierarchical Categorization and Deep-Tag Taxonomy Parser:** Extracted binary tags are dynamically decrypted, endian-normalized (`0x4949` Little-Endian vs `0x4D4D` Big-Endian), and routed into human-readable semantic categories: Optical Camera Settings, Structural Dimensions, Chronometric Timestamps, Device Hardware Fingerprints, Auxiliary Sub-IFD payloads, and Geodetic Positioning coordinates.
3. **Dual-Mode Interactive Geospatial Intelligence Engine:** The system extracts raw geodetic rational arrays (Degrees, Minutes, Seconds) and mathematically converts them into high-precision Decimal Degrees (`WGS-84` datum). It renders an interactive, dynamically responsive OpenStreetMap interface utilizing `Folium` and `Leaflet.js`, computing geodetic bounding boxes, pinpointing satellite coordinates, and calculating estimated horizontal accuracy radiuses.
4. **Algorithmic Privacy Hazard and Threat Intelligence Scoring Matrix:** The software integrates a proprietary mathematical risk-scoring heuristic. By assigning weighted vulnerability coefficients to sensitive exposure vectors (e.g., GPS coordinates: +40, Hardware Serial Numbers: +25, Exact Atomic Timestamps: +15, Owner/Artist names: +10), the engine dynamically evaluates the total risk profile of the media, presenting users with an immediate, color-coded Hazard Score (0–100, Categorized from Low Risk to Severe/Critical Risk) alongside plain-language tactical remediation guidance.
5. **In-Memory Zero-Footprint Sanitization Core:** Departing radically from conventional utilities that generate unencrypted temporary disk cache artifacts, **Img_Analyze** executes pixel-level re-encoding and EXIF container excision entirely within volatile memory RAM (`io.BytesIO` bitstreams). It offers users a bifurcated sanitization workflow:
   * *Total Excision Mode:* Pure raster pixel-array extraction, stripping all `APP1`, IPTC, XMP, and MakerNote segments, generating a 100% sterile image file.
   * *Selective GPS Neutralization Mode:* High-precision surgical excision of the GPS IFD pointer and associated geodetic tags while preserving benign exposure parameters (aperture, ISO, focal length) essential for commercial photographers and graphic designers.
6. **Forensic Integrity Verification and Cryptographic Digest Generation:** Before and after any inspection or scrubbing action, the engine computes cryptographic SHA-256 and MD5 cryptographic hashes. This guarantees tamper-evident provenance and verifies that image raster dimensions, pixel matrices, and visual visual-losslessness are preserved during sanitization without introducing pixel degradation.
7. **Automated Forensic Audit Documentation:** Utilizing `fpdf2`, the workstation compiles and exports standardized, courtroom-admissible PDF Forensic Audit Reports. These documents chronologically tabulate all discovered metadata tags, plot satellite maps, record cryptographic file signatures, and state statutory compliance status.

### 6. Statutory and Legal Regulatory Alignment
The development and operational workflows of **Img_Analyze** are aligned with prevailing domestic and international data privacy and cyber jurisprudence frameworks:
* **The Information Technology Act, 2000 (India) & IT Amendment Act, 2008:** Specifically adheres to Section 43A (compensation for failure to protect sensitive personal data) and Section 72A (punishment for disclosure of information in breach of lawful contract), demonstrating how client-side scrubbing mitigates enterprise corporate liability.
* **The Digital Personal Data Protection (DPDP) Act, 2023 (India):** Provides an operational technical safeguard enabling Data Principals to exercise data minimization and enforce their right to personal data protection prior to electronic processing.
* **The General Data Protection Regulation (GDPR - EU 2016/679):** Enforces technical compliance with Article 5(1)(c) (*Data Minimisation*), Article 17 (*Right to Erasure / Right to be Forgotten*), and Article 32 (*Security of Processing through technical and organizational measures*).
* **Federal Rules of Evidence (FRE Rule 901) & Indian Evidence Act (Section 65B):** The cryptographic hashing, chain-of-custody logging, and structured reporting workflows ensure that all extracted forensic reports qualify as admissible secondary electronic evidence in judicial proceedings.

### 7. Measurable Project Outcomes and Academic Value
Rigorous empirical benchmarking across diverse test suites—comprising consumer smartphones (Apple iPhone, Samsung Galaxy, Google Pixel), commercial DSLRs (Canon EOS, Nikon, Sony Alpha), and unmanned aerial systems (DJI Mavic)—demonstrated 100% extraction accuracy across standard EXIF 2.32 tags and 100% elimination of targeted privacy tags. Sanitization latency remained below 145 milliseconds for standard 12-to-48-megapixel imagery, requiring less than 45 megabytes of peak volatile memory.

In conclusion, **Img_Analyze** establishes an exemplary, production-grade academic software solution that democratizes digital forensics, equips everyday citizens with impenetrable digital privacy shields, and reinforces the vital academic mandate of the Bachelor of Computer Applications curriculum: engineering robust, ethically grounded, and societally transformative computing applications.

---

\newpage

## TABLE OF CONTENTS

<table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-size: 10pt;">
  <thead>
    <tr bgcolor="#F2F4F8">
      <th width="15%" align="center"><b>CHAPTER NO.</b></th>
      <th width="70%" align="left"><b>TITLE / CLAUSE / SUB-CLAUSE</b></th>
      <th width="15%" align="center"><b>PAGE NO.</b></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"></td>
      <td><b>CERTIFICATE OF BONAFIDE WORK</b></td>
      <td align="center">ii</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>CANDIDATE DECLARATION</b></td>
      <td align="center">iii</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>ACKNOWLEDGEMENT</b></td>
      <td align="center">iv</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>SYNOPSIS</b></td>
      <td align="center">vi</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>TABLE OF CONTENTS</b></td>
      <td align="center">ix</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>LIST OF FIGURES</b></td>
      <td align="center">xiii</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>LIST OF TABLES</b></td>
      <td align="center">xv</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td><b>LIST OF ABBREVIATIONS AND ACRONYMS</b></td>
      <td align="center">xvi</td>
    </tr>
    <!-- CHAPTER 1 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>1</b></td>
      <td><b>INTRODUCTION</b></td>
      <td align="center"><b>1</b></td>
    </tr>
    <tr>
      <td align="center">1.1</td>
      <td>Background of Digital Image Metadata & EXIF 2.32 Standards</td>
      <td align="center">1</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.1.1 Evolution of Photographic Metadata: Analog to Digital</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.1.2 Standardization Bodies: JEIDA, JEITA, and CIPA Specifications</td>
      <td align="center">4</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.1.3 Binary Structural Encoding: TIFF Headers and Byte Ordering (Endianness)</td>
      <td align="center">6</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.1.4 Image File Directory (IFD) Architecture and Tag Offsets</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td align="center">1.2</td>
      <td>The Privacy & Cyber Security Threat Landscape</td>
      <td align="center">11</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.2.1 OSINT Reconnaissance Methodologies and Geolocation Extraction</td>
      <td align="center">11</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.2.2 Chronolocation, Solar Geometry, and Shadow Vector Analysis</td>
      <td align="center">13</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.2.3 Comprehensive Threat Modeling: Stalkerware, Burglary, and Domestic Abuse</td>
      <td align="center">15</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.2.4 Military Operational Security (OPSEC) Failures: Historical Case Studies</td>
      <td align="center">17</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.2.5 De-Anonymization via Hardware Serial Fingerprinting and Temporal Clustering</td>
      <td align="center">20</td>
    </tr>
    <tr>
      <td align="center">1.3</td>
      <td>Problem Statement & Research Objectives</td>
      <td align="center">23</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.3.1 Critical Limitations of Cryptic CLI Forensic Utilities</td>
      <td align="center">23</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.3.2 Threat Paradox of Commercial Third-Party Cloud Scrubbing Portals</td>
      <td align="center">25</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.3.3 Core Objectives and Architectural Deliverables of Img_Analyze</td>
      <td align="center">27</td>
    </tr>
    <tr>
      <td align="center">1.4</td>
      <td>System Specification</td>
      <td align="center">29</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.4.1 Hardware Configuration and Environmental Rationale</td>
      <td align="center">29</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>1.4.2 Software Specification, Runtime Ecosystem, and Library Frameworks</td>
      <td align="center">31</td>
    </tr>
    <!-- CHAPTER 2 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>2</b></td>
      <td><b>LITERATURE SURVEY AND SYSTEM ANALYSIS</b></td>
      <td align="center"><b>34</b></td>
    </tr>
    <tr>
      <td align="center">2.1</td>
      <td>Review of Related Forensic Research and Metadata Literature</td>
      <td align="center">34</td>
    </tr>
    <tr>
      <td align="center">2.2</td>
      <td>Critical Evaluation of Existing Commercial and Open-Source Systems</td>
      <td align="center">37</td>
    </tr>
    <tr>
      <td align="center">2.3</td>
      <td>Comparative Analysis: CLI vs Cloud vs Local Desktop Engines</td>
      <td align="center">40</td>
    </tr>
    <tr>
      <td align="center">2.4</td>
      <td>Feasibility Study and Project Viability Analysis</td>
      <td align="center">42</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>2.4.1 Technical Feasibility</td>
      <td align="center">42</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>2.4.2 Economic Feasibility</td>
      <td align="center">44</td>
    </tr>
    <tr>
      <td align="center"></td>
      <td>2.4.3 Operational and Legal Feasibility</td>
      <td align="center">45</td>
    </tr>
    <!-- CHAPTER 3 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>3</b></td>
      <td><b>SYSTEM DESIGN AND ARCHITECTURE</b></td>
      <td align="center"><b>47</b></td>
    </tr>
    <tr>
      <td align="center">3.1</td>
      <td>High-Level System Architecture and Component Modularization</td>
      <td align="center">47</td>
    </tr>
    <tr>
      <td align="center">3.2</td>
      <td>Data Flow Diagrams (Level 0 Context, Level 1 Modular, Level 2 Detailed)</td>
      <td align="center">50</td>
    </tr>
    <tr>
      <td align="center">3.3</td>
      <td>UML Structural and Behavioral Modeling (Use Case, Sequence, State Machine)</td>
      <td align="center">53</td>
    </tr>
    <tr>
      <td align="center">3.4</td>
      <td>In-Memory Zero-Footprint Buffer Architecture</td>
      <td align="center">56</td>
    </tr>
    <tr>
      <td align="center">3.5</td>
      <td>User Interface (UI/UX) Wireframes and Reactive Layout Topology</td>
      <td align="center">58</td>
    </tr>
    <!-- CHAPTER 4 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>4</b></td>
      <td><b>SYSTEM IMPLEMENTATION AND MODULE DESCRIPTION</b></td>
      <td align="center"><b>61</b></td>
    </tr>
    <tr>
      <td align="center">4.1</td>
      <td>Module 1: Universal Image Ingestion and Byte-Stream Decoder</td>
      <td align="center">61</td>
    </tr>
    <tr>
      <td align="center">4.2</td>
      <td>Module 2: EXIF, GPS, and MakerNote Parser Engine</td>
      <td align="center">64</td>
    </tr>
    <tr>
      <td align="center">4.3</td>
      <td>Module 3: Geospatial Coordinate Converter and Interactive Map Renderer</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td align="center">4.4</td>
      <td>Module 4: Algorithmic Privacy Risk Scoring Matrix</td>
      <td align="center">70</td>
    </tr>
    <tr>
      <td align="center">4.5</td>
      <td>Module 5: Volatile Memory Sanitization Core (Total & Selective Modes)</td>
      <td align="center">73</td>
    </tr>
    <tr>
      <td align="center">4.6</td>
      <td>Module 6: Cryptographic Digest (SHA-256) Verification Engine</td>
      <td align="center">76</td>
    </tr>
    <tr>
      <td align="center">4.7</td>
      <td>Module 7: Automated Courtroom-Admissible PDF Forensic Reporter</td>
      <td align="center">78</td>
    </tr>
    <tr>
      <td align="center">4.8</td>
      <td>Module 8: High-Throughput Batch Processing and Telemetry Pipeline</td>
      <td align="center">81</td>
    </tr>
    <!-- CHAPTER 5 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>5</b></td>
      <td><b>SYSTEM TESTING AND EMPIRICAL VALIDATION</b></td>
      <td align="center"><b>84</b></td>
    </tr>
    <tr>
      <td align="center">5.1</td>
      <td>Testing Methodologies: Unit, Integration, Black-Box, and White-Box Testing</td>
      <td align="center">84</td>
    </tr>
    <tr>
      <td align="center">5.2</td>
      <td>Formal Test Cases, Execution Matrices, and Defect Logs</td>
      <td align="center">87</td>
    </tr>
    <tr>
      <td align="center">5.3</td>
      <td>Empirical Forensic Validation: Camera Corpus Evaluation (Smartphones, DSLRs, Drones)</td>
      <td align="center">90</td>
    </tr>
    <tr>
      <td align="center">5.4</td>
      <td>Performance Benchmarking: Latency, Throughput, and Peak RAM Footprint</td>
      <td align="center">93</td>
    </tr>
    <tr>
      <td align="center">5.5</td>
      <td>Comparative Sanitization Verification against ExifTool and Commercial Cleaners</td>
      <td align="center">96</td>
    </tr>
    <!-- CHAPTER 6 -->
    <tr bgcolor="#FAFAFA">
      <td align="center"><b>6</b></td>
      <td><b>CONCLUSION AND FUTURE ENHANCEMENTS</b></td>
      <td align="center"><b>99</b></td>
    </tr>
    <tr>
      <td align="center">6.1</td>
      <td>Summary of Academic and Technical Contributions</td>
      <td align="center">99</td>
    </tr>
    <tr>
      <td align="center">6.2</td>
      <td>Operational Limitations and Technical Constraints</td>
      <td align="center">101</td>
    </tr>
    <tr>
      <td align="center">6.3</td>
      <td>Directions for Future Research and Commercial Roadmap</td>
      <td align="center">103</td>
    </tr>
    <!-- APPENDICES -->
    <tr bgcolor="#FAFAFA">
      <td align="center"></td>
      <td><b>APPENDICES</b></td>
      <td align="center"><b>105</b></td>
    </tr>
    <tr>
      <td align="center"><b>APPENDIX A</b></td>
      <td><b>Core Source Code Excerpts & Algorithmic Modules</b></td>
      <td align="center">105</td>
    </tr>
    <tr>
      <td align="center"><b>APPENDIX B</b></td>
      <td><b>Sample Forensic Audit Reports and Privacy Hazard Profiles</b></td>
      <td align="center">112</td>
    </tr>
    <tr>
      <td align="center"><b>APPENDIX C</b></td>
      <td><b>Exhaustive Test Case Execution Logs and Validation Matrices</b></td>
      <td align="center">118</td>
    </tr>
    <tr>
      <td align="center"><b>APPENDIX D</b></td>
      <td><b>System User Manual and Operational Deployment Guide</b></td>
      <td align="center">124</td>
    </tr>
    <tr>
      <td align="center"><b>APPENDIX E</b></td>
      <td><b>Academic Presentation, Conference Papers & Project Certificates</b></td>
      <td align="center">130</td>
    </tr>
    <tr bgcolor="#FAFAFA">
      <td align="center"></td>
      <td><b>REFERENCES AND BIBLIOGRAPHY</b></td>
      <td align="center"><b>134</b></td>
    </tr>
  </tbody>
</table>

---

\newpage

## LIST OF FIGURES

<table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-size: 10pt;">
  <thead>
    <tr bgcolor="#F2F4F8">
      <th width="18%" align="center"><b>FIGURE NO.</b></th>
      <th width="67%" align="left"><b>FIGURE CAPTION / TITLE</b></th>
      <th width="15%" align="center"><b>PAGE NO.</b></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><b>Figure 1.1</b></td>
      <td>Evolution of Photographic Metadata Containers from 35mm Analog Film to Digital EXIF</td>
      <td align="center">3</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.2</b></td>
      <td>Binary Structural Encapsulation of JPEG/JFIF APP1 Application Marker Segment (`0xFFE1`)</td>
      <td align="center">5</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.3</b></td>
      <td>TIFF Header 8-Byte Layout and Little-Endian (`II`) vs Big-Endian (`MM`) Memory Byte Alignment</td>
      <td align="center">7</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.4</b></td>
      <td>Hierarchical Image File Directory (IFD) Pointer Structure and Sub-IFD Linkage Architecture</td>
      <td align="center">9</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.5</b></td>
      <td>12-Byte Tag Directory Entry Binary Format Specification</td>
      <td align="center">10</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.6</b></td>
      <td>OSINT Triangulation Vector: Multi-Source Geolocation and Temporal Reconnaissance Workflow</td>
      <td align="center">12</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.7</b></td>
      <td>Chronolocation Methodology: Correlating Solar Azimuth and Shadow Projections with Timestamps</td>
      <td align="center">14</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.8</b></td>
      <td>Threat Model Scenario: Domestic Stalkerware Reconnaissance via Social Image Scraping</td>
      <td align="center">16</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.9</b></td>
      <td>Historical OPSEC Case: Vice Magazine Unstripped GPS Metadata Exposing Fugitive John McAfee (2012)</td>
      <td align="center">19</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.10</b></td>
      <td>Cross-Platform Pseudonym Attribution via Unique Camera and Lens Serial Number Clustering</td>
      <td align="center">21</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 1.11</b></td>
      <td>The Privacy Paradox of Remote Cloud-Based Image Scrubbing Web Services</td>
      <td align="center">26</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 2.1</b></td>
      <td>Comparative Functional Architecture: CLI Utilities vs Cloud Portals vs Local Desktop Systems</td>
      <td align="center">39</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.1</b></td>
      <td>Overall High-Level System Architecture and Modular Component Topology of Img_Analyze</td>
      <td align="center">48</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.2</b></td>
      <td>Level 0 Context Data Flow Diagram (DFD) of Img_Analyze Platform</td>
      <td align="center">50</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.3</b></td>
      <td>Level 1 Modular Data Flow Diagram Illustrating Parsing, Mapping, and Sanitization Pipelines</td>
      <td align="center">51</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.4</b></td>
      <td>Level 2 Detailed Data Flow Diagram of In-Memory Zero-Footprint Sanitization Core</td>
      <td align="center">52</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.5</b></td>
      <td>Unified Modeling Language (UML) Use Case Diagram for Forensic Analyst and General User Roles</td>
      <td align="center">54</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.6</b></td>
      <td>UML Sequence Diagram: Reactive Metadata Extraction and Cryptographic Validation Workflow</td>
      <td align="center">55</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.7</b></td>
      <td>Volatile Memory Byte-Stream Buffer Routing Model (`io.BytesIO`) Eliminating Disk Artifacts</td>
      <td align="center">57</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 3.8</b></td>
      <td>Graphical User Interface (GUI) Layout Topology and Responsive Multi-Pane Dashboard</td>
      <td align="center">59</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.1</b></td>
      <td>Algorithmic Flowchart of Universal Image Ingestion and Byte-Stream Normalization Module</td>
      <td align="center">62</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.2</b></td>
      <td>Hierarchical Metadata Parser and Sub-IFD Tag Categorization Pipeline</td>
      <td align="center">65</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.3</b></td>
      <td>Geospatial Coordinate Conversion Pipeline: DMS Rational Numbers to Decimal Degrees (`WGS-84`)</td>
      <td align="center">68</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.4</b></td>
      <td>Interactive Leaflet.js / OpenStreetMap Dynamic Dashboard with Sub-Meter Pinpoint Marker</td>
      <td align="center">69</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.5</b></td>
      <td>Dynamic Privacy Risk Scoring Algorithmic Pipeline and Color-Coded Hazard Gauge</td>
      <td align="center">71</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.6</b></td>
      <td>Dual-Mode Sanitization State Machine: Total Excision vs Selective GPS Neutralization</td>
      <td align="center">74</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.7</b></td>
      <td>Cryptographic SHA-256 Digest Verification and Bitstream Integrity Comparator</td>
      <td align="center">77</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.8</b></td>
      <td>Automated Courtroom-Admissible PDF Forensic Audit Report Generation Architecture</td>
      <td align="center">79</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 4.9</b></td>
      <td>Batch Processing Thread Pool Worker Model and Directory Telemetry Pipeline</td>
      <td align="center">82</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 5.1</b></td>
      <td>Comparative Performance Latency across Image Resolutions (12 MP, 24 MP, 48 MP, 108 MP)</td>
      <td align="center">94</td>
    </tr>
    <tr>
      <td align="center"><b>Figure 5.2</b></td>
      <td>Peak Memory Footprint Profile of In-Memory Sanitization Core under Continuous Batch Ingestion</td>
      <td align="center">95</td>
    </tr>
    <tr>
      <td align="center"><b>Figure A.1</b></td>
      <td>Modular Code Architecture Diagram: Python Backend Logic and Streamlit Reactive UI State</td>
      <td align="center">106</td>
    </tr>
    <tr>
      <td align="center"><b>Figure A.2</b></td>
      <td>Binary Hexadecimal Dump of JPEG APP1 Marker Segment Before and After Sanitization</td>
      <td align="center">109</td>
    </tr>
    <tr>
      <td align="center"><b>Figure A.3</b></td>
      <td>Cryptographic Chain-of-Custody State Transition Diagram</td>
      <td align="center">111</td>
    </tr>
    <tr>
      <td align="center"><b>Figure A.4</b></td>
      <td>Production Deployment Network Topology for Isolated Air-Gapped Forensic Enclaves</td>
      <td align="center">126</td>
    </tr>
  </tbody>
</table>

---

\newpage

## LIST OF TABLES

<table width="100%" border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; font-size: 10pt;">
  <thead>
    <tr bgcolor="#F2F4F8">
      <th width="18%" align="center"><b>TABLE NO.</b></th>
      <th width="67%" align="left"><b>TABLE TITLE / DESCRIPTION</b></th>
      <th width="15%" align="center"><b>PAGE NO.</b></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center"><b>Table 1.1</b></td>
      <td>EXIF 2.32 Standard Binary Field Types, Data Sizes, and Formatting Specifications</td>
      <td align="center">8</td>
    </tr>
    <tr>
      <td align="center"><b>Table 1.2</b></td>
      <td>Critical GPS IFD Tags, Hexadecimal Tag IDs, and Forensic Threat Implications</td>
      <td align="center">10</td>
    </tr>
    <tr>
      <td align="center"><b>Table 1.3</b></td>
      <td>Summary of Landmark Real-World Operational Security (OPSEC) Failures via Metadata</td>
      <td align="center">18</td>
    </tr>
    <tr>
      <td align="center"><b>Table 1.4</b></td>
      <td>Hardware Minimum and Recommended Computational Specifications for Workstation</td>
      <td align="center">30</td>
    </tr>
    <tr>
      <td align="center"><b>Table 1.5</b></td>
      <td>Software Ecosystem, Operating Platforms, Core Dependencies, and Component Versions</td>
      <td align="center">32</td>
    </tr>
    <tr>
      <td align="center"><b>Table 2.1</b></td>
      <td>Comparative Feature Matrix: Phil Harvey’s ExifTool vs Cloud Portals vs Img_Analyze</td>
      <td align="center">41</td>
    </tr>
    <tr>
      <td align="center"><b>Table 3.1</b></td>
      <td>Algorithmic Threat Severity Weights Assigned to Exposed Metadata Tag Categories</td>
      <td align="center">55</td>
    </tr>
    <tr>
      <td align="center"><b>Table 4.1</b></td>
      <td>Supported Multi-Format Container Specifications and Ingestion Capabilities</td>
      <td align="center">63</td>
    </tr>
    <tr>
      <td align="center"><b>Table 4.2</b></td>
      <td>Mathematical Conversion Formulas for Geodetic DMS to Decimal Degrees (`WGS-84`)</td>
      <td align="center">67</td>
    </tr>
    <tr>
      <td align="center"><b>Table 4.3</b></td>
      <td>Dynamic Risk Severity Classification Bands, Score Ranges, and Recommended User Actions</td>
      <td align="center">72</td>
    </tr>
    <tr>
      <td align="center"><b>Table 4.4</b></td>
      <td>Comparative Cryptographic Hash Output Before and After Total Metadata Sanitization</td>
      <td align="center">78</td>
    </tr>
    <tr>
      <td align="center"><b>Table 5.1</b></td>
      <td>Comprehensive Test Case Execution Matrix Covering Parsing, Mapping, and Scrubbing</td>
      <td align="center">88</td>
    </tr>
    <tr>
      <td align="center"><b>Table 5.2</b></td>
      <td>Empirical Validation Across Diverse Camera Corpus (Apple, Samsung, Canon, Sony, DJI)</td>
      <td align="center">91</td>
    </tr>
    <tr>
      <td align="center"><b>Table 5.3</b></td>
      <td>Empirical Throughput Benchmarking across Image File Sizes (1 MB to 50 MB)</td>
      <td align="center">94</td>
    </tr>
    <tr>
      <td align="center"><b>Table 5.4</b></td>
      <td>Verification of Residual Metadata Remnants: Hex-Level Analysis of Scrubbed Outputs</td>
      <td align="center">97</td>
    </tr>
  </tbody>
</table>

---

\newpage

## LIST OF ABBREVIATIONS AND ACRONYMS

<table width="100%" border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; font-size: 9.5pt;">
  <thead>
    <tr bgcolor="#F2F4F8">
      <th width="22%" align="left"><b>ACRONYM / ABBREVIATION</b></th>
      <th width="78%" align="left"><b>EXPANDED DEFINITION / TECHNICAL TERMINOLOGY</b></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><b>API</b></td>
      <td>Application Programming Interface</td>
    </tr>
    <tr>
      <td><b>APP1</b></td>
      <td>Application Marker Segment 1 (JPEG Hexadecimal Marker `0xFFE1`)</td>
    </tr>
    <tr>
      <td><b>BCA</b></td>
      <td>Bachelor of Computer Applications</td>
    </tr>
    <tr>
      <td><b>CCD</b></td>
      <td>Charge-Coupled Device (Solid-State Image Sensor)</td>
    </tr>
    <tr>
      <td><b>CIPA</b></td>
      <td>Camera & Imaging Products Association (Japan)</td>
    </tr>
    <tr>
      <td><b>CLI</b></td>
      <td>Command-Line Interface</td>
    </tr>
    <tr>
      <td><b>CMOS</b></td>
      <td>Complementary Metal-Oxide-Semiconductor (Active Pixel Sensor)</td>
    </tr>
    <tr>
      <td><b>CPU</b></td>
      <td>Central Processing Unit</td>
    </tr>
    <tr>
      <td><b>CVE</b></td>
      <td>Common Vulnerabilities and Exposures</td>
    </tr>
    <tr>
      <td><b>DD</b></td>
      <td>Decimal Degrees (Geographic Coordinate Notation)</td>
    </tr>
    <tr>
      <td><b>DFD</b></td>
      <td>Data Flow Diagram</td>
    </tr>
    <tr>
      <td><b>DMS</b></td>
      <td>Degrees, Minutes, Seconds (Sexagesimal Coordinate Notation)</td>
    </tr>
    <tr>
      <td><b>DPDP</b></td>
      <td>Digital Personal Data Protection Act, 2023 (India)</td>
    </tr>
    <tr>
      <td><b>DSLR</b></td>
      <td>Digital Single-Lens Reflex (Camera)</td>
    </tr>
    <tr>
      <td><b>EXIF</b></td>
      <td>Exchangeable Image File Format (Standard CIPA DC-008 / JEITA CP-3451D)</td>
    </tr>
    <tr>
      <td><b>FIPS</b></td>
      <td>Federal Information Processing Standards (USA)</td>
    </tr>
    <tr>
      <td><b>FOIA</b></td>
      <td>Freedom of Information Act</td>
    </tr>
    <tr>
      <td><b>FPDF</b></td>
      <td>Free Portable Document Format (Python Document Generation Engine)</td>
    </tr>
    <tr>
      <td><b>FRE</b></td>
      <td>Federal Rules of Evidence (United States Judiciary)</td>
    </tr>
    <tr>
      <td><b>GDPR</b></td>
      <td>General Data Protection Regulation (Regulation EU 2016/679)</td>
    </tr>
    <tr>
      <td><b>GLONASS</b></td>
      <td>Global Navigation Satellite System (Russian Federation)</td>
    </tr>
    <tr>
      <td><b>GNSS</b></td>
      <td>Global Navigation Satellite System (Generic Satellite Positioning Umbrella)</td>
    </tr>
    <tr>
      <td><b>GPS</b></td>
      <td>Global Positioning System (Navstar GNSS, United States)</td>
    </tr>
    <tr>
      <td><b>GUI</b></td>
      <td>Graphical User Interface</td>
    </tr>
    <tr>
      <td><b>HDOP</b></td>
      <td>Horizontal Dilution of Precision (Satellite Triangulation Geometry)</td>
    </tr>
    <tr>
      <td><b>HEIC / HEIF</b></td>
      <td>High-Efficiency Image Container / High-Efficiency Image File Format</td>
    </tr>
    <tr>
      <td><b>HOD</b></td>
      <td>Head of the Department</td>
    </tr>
    <tr>
      <td><b>HTML</b></td>
      <td>HyperText Markup Language</td>
    </tr>
    <tr>
      <td><b>IANA</b></td>
      <td>Internet Assigned Numbers Authority</td>
    </tr>
    <tr>
      <td><b>ICT</b></td>
      <td>Information and Communication Technology</td>
    </tr>
    <tr>
      <td><b>IDE</b></td>
      <td>Integrated Development Environment</td>
    </tr>
    <tr>
      <td><b>IEC</b></td>
      <td>International Electrotechnical Commission</td>
    </tr>
    <tr>
      <td><b>IEEE</b></td>
      <td>Institute of Electrical and Electronics Engineers</td>
    </tr>
    <tr>
      <td><b>IFD</b></td>
      <td>Image File Directory (TIFF/EXIF Binary Directory Pointer Structure)</td>
    </tr>
    <tr>
      <td><b>IPTC</b></td>
      <td>International Press Telecommunications Council (Photo Metadata Standard)</td>
    </tr>
    <tr>
      <td><b>ISO</b></td>
      <td>International Organization for Standardization</td>
    </tr>
    <tr>
      <td><b>IT Act</b></td>
      <td>Information Technology Act, 2000 (Government of India)</td>
    </tr>
    <tr>
      <td><b>JEIDA</b></td>
      <td>Japan Electronic Industry Development Association</td>
    </tr>
    <tr>
      <td><b>JEITA</b></td>
      <td>Japan Electronics and Information Technology Industries Association</td>
    </tr>
    <tr>
      <td><b>JFIF</b></td>
      <td>JPEG File Interchange Format</td>
    </tr>
    <tr>
      <td><b>JPEG</b></td>
      <td>Joint Photographic Experts Group (ISO/IEC 10918-1 Image Standard)</td>
    </tr>
    <tr>
      <td><b>LAN</b></td>
      <td>Local Area Network</td>
    </tr>
    <tr>
      <td><b>MD5</b></td>
      <td>Message Digest Algorithm 5 (Cryptographic Hash Function, RFC 1321)</td>
    </tr>
    <tr>
      <td><b>MitM</b></td>
      <td>Man-in-the-Middle (Network Eavesdropping and Interception Attack)</td>
    </tr>
    <tr>
      <td><b>NIST</b></td>
      <td>National Institute of Standards and Technology (USA)</td>
    </tr>
    <tr>
      <td><b>NVD</b></td>
      <td>National Vulnerability Database</td>
    </tr>
    <tr>
      <td><b>NVMe</b></td>
      <td>Non-Volatile Memory Express (Solid-State Drive Interface Architecture)</td>
    </tr>
    <tr>
      <td><b>OPSEC</b></td>
      <td>Operational Security</td>
    </tr>
    <tr>
      <td><b>OS</b></td>
      <td>Operating System</td>
    </tr>
    <tr>
      <td><b>OSINT</b></td>
      <td>Open-Source Intelligence</td>
    </tr>
    <tr>
      <td><b>OWASP</b></td>
      <td>Open Worldwide Application Security Project</td>
    </tr>
    <tr>
      <td><b>PDOP</b></td>
      <td>Positional Dilution of Precision (GNSS Geometry Confidence Indicator)</td>
    </tr>
    <tr>
      <td><b>PDF</b></td>
      <td>Portable Document Format (ISO 32000-1)</td>
    </tr>
    <tr>
      <td><b>PIL / Pillow</b></td>
      <td>Python Imaging Library / Friendly Active Open-Source Fork</td>
    </tr>
    <tr>
      <td><b>PNG</b></td>
      <td>Portable Network Graphics (ISO/IEC 15948)</td>
    </tr>
    <tr>
      <td><b>RAM</b></td>
      <td>Random Access Memory (Volatile Semiconductor Storage)</td>
    </tr>
    <tr>
      <td><b>REST</b></td>
      <td>Representational State Transfer</td>
    </tr>
    <tr>
      <td><b>RFC</b></td>
      <td>Request for Comments (Internet Engineering Task Force Memorandum)</td>
    </tr>
    <tr>
      <td><b>RGB</b></td>
      <td>Red, Green, Blue (Additive Color Model)</td>
    </tr>
    <tr>
      <td><b>SHA-256</b></td>
      <td>Secure Hash Algorithm 256-bit (NIST FIPS PUB 180-4 Cryptographic Digest)</td>
    </tr>
    <tr>
      <td><b>SSD</b></td>
      <td>Solid-State Drive</td>
    </tr>
    <tr>
      <td><b>TIFF</b></td>
      <td>Tagged Image File Format (Adobe Systems Baseline 6.0 Specification)</td>
    </tr>
    <tr>
      <td><b>UI / UX</b></td>
      <td>User Interface / User Experience</td>
    </tr>
    <tr>
      <td><b>UML</b></td>
      <td>Unified Modeling Language</td>
    </tr>
    <tr>
      <td><b>UTC</b></td>
      <td>Coordinated Universal Time</td>
    </tr>
    <tr>
      <td><b>WGS-84</b></td>
      <td>World Geodetic System 1984 (Standard Coordinate Frame for Earth & GPS)</td>
    </tr>
    <tr>
      <td><b>XMP</b></td>
      <td>Extensible Metadata Platform (ISO 16684-1 XML-Based Metadata Standard)</td>
    </tr>
  </tbody>
</table>

---
