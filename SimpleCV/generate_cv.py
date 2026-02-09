import markdown
import os
import subprocess
import shutil
from pypdf import PdfReader, PdfWriter

def generate_cv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_file = os.path.join(base_dir, 'CV.md')
    html_file = os.path.join(base_dir, 'CV.html')
    pdf_file = os.path.join(base_dir, 'CV.pdf')
    png_file = os.path.join(base_dir, 'CV.png')

    # Modern CSS with Grid - Clean & Professional
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * { box-sizing: border-box; }

    body {
        font-family: 'Inter', sans-serif;
        margin: 0;
        padding: 0;
        background-color: #fff;
        color: #334155;
        font-size: 12.8px; /* Balanced size */
        line-height: 1.45;
        width: 210mm;
        height: 297mm;
        overflow: hidden; /* Ensure single page */
    }

    /* Layout: Sidebar (Left) + Main (Right) */
    .page-container {
        display: grid;
        grid-template-columns: 75mm 1fr;
        height: 100%;
    }

    /* Sidebar Styling */
    .sidebar {
        background-color: #f8fafc;
        color: #334155;
        padding: 15px 25px; /* Reduced padding to shift up */
        display: flex;
        flex-direction: column;
        gap: 12px; /* Reduced gap */
        border-right: 1px solid #e2e8f0;
    }

    .profile-pic-container {
        width: 125px;
        height: 125px;
        border-radius: 50%;
        border: 4px solid #fff;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        margin: 0 auto;
    }

    .profile-pic {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .contact-section h1 {
        font-size: 23px;
        font-weight: 800;
        color: #1e293b;
        margin: 0 0 5px 0;
        text-align: center;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    .subtitle {
        text-align: center;
        color: #2563eb;
        font-weight: 600;
        margin-bottom: 15px;
        display: block;
        font-size: 13.5px;
    }

    .contact-details {
        display: flex;
        flex-direction: column;
        gap: 7px;
        font-size: 11.5px;
    }

    .contact-details p { margin: 0; display: flex; align-items: center; gap: 8px; }
    .contact-details a { 
        color: #475569; 
        text-decoration: none; 
        font-weight: 500;
        border-bottom: 1px dotted #94a3b8;
    }

    .section-title {
        font-size: 12.5px;
        text-transform: uppercase;
        letter-spacing: 1.1px;
        color: #64748b;
        font-weight: 700;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 5px;
        margin-bottom: 10px;
    }

    /* Thesis Image Styling */
    .thesis-sidebar-container {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        background: #fff;
        padding: 9px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    
    .thesis-sidebar-container img {
        width: 100%;
        height: auto;
        display: block;
        border: 1px solid #cbd5e1;
        margin-bottom: 6px;
    }
    
    .thesis-header {
        font-size: 12px;
        font-weight: 700;
        color: #2563eb;
        text-align: center;
        margin-bottom: 6px;
        line-height: 1.3;
    }

    .thesis-caption {
        font-size: 10px;
        color: #64748b;
        text-align: center;
        font-style: italic;
        line-height: 1.3;
    }

    /* Main Content Styling */
    .main-content {
        padding: 30px 35px; /* Increased vertical padding */
        display: flex;
        flex-direction: column;
        gap: 18px; /* Balanced gap */
    }

    .main-section {
        margin-bottom: 5px;
    }
    
    .main-title {
        font-size: 15.5px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 5px;
    }

    .about-text {
        text-align: left;
        margin-bottom: 10px;
        color: #334155;
        text-align: justify;
    }

    .project-item, .job-item {
        margin-bottom: 13px; /* Slightly increased */
    }

    .item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 3px;
    }

    .item-title {
        font-weight: 700;
        color: #1e293b;
        font-size: 14px;
    }

    .item-date {
        color: #64748b;
        font-size: 11px;
        font-weight: 500;
        white-space: nowrap; 
        background: #f1f5f9;
        padding: 2px 7px;
        border-radius: 4px;
    }

    .item-desc {
        color: #475569;
        font-size: 12.5px; /* Restored size */
        margin: 0;
    }
    
    a.link-style {
        color: #2563eb;
        text-decoration: none;
    }

    /* Skills Grid */
    .skills-ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .skills-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 14px;
    }
    .skills-ul li {
        font-size: 12.5px;
    }
    .skills-ul strong { color: #0f172a; font-weight: 600; }

    /* Print Specifics */
    @media print {
        @page { margin: 0; }
        body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Tom de Groot - CV</title>
        <style>{css}</style>
    </head>
    <body>
        <div class="page-container">
            <!-- SIDEBAR -->
            <div class="sidebar">
                <div class="profile-pic-container">
                    <img src="Profile_pic.jpg" class="profile-pic" alt="Profile">
                </div>
                
                <div class="contact-section">
                    <h1>Tom de Groot</h1>
                    <span class="subtitle">Chemistry - Mathematics <br> Programming - AI</span>
                    
                    <div class="contact-details">
                        <p><strong>Born:</strong> 30-03-2004</p>
                        <p>Grijpskerk, NL</p>
                        <p>Herestraat 45, 9843 AJ</p>
                        <p><a href="tel:+31631490416">+31 6 314 90 416</a></p>
                        <p><a href="mailto:tomthegreatest04@gmail.com">tomthegreatest04@gmail.com</a></p>
                        <p><a href="https://github.com/Tomodovodoo">github.com/Tomodovodoo</a></p>
                        <p><a href="https://x.com/Tomodovodoo">x.com/Tomodovodoo</a></p>
                    </div>
                </div>

                <!-- THESIS IMAGE IN SIDEBAR (High Up) -->
                <div class="thesis-sidebar-container">
                     <div class="thesis-header">Research Showcase</div>
                    <img src="Thesis_page.png" alt="Thesis Excerpt">
                    <div class="thesis-caption">
                         <strong>Bachelor Thesis:</strong> Evaluating and Optimizing NMR Prediction with GNNs (Pollice Research Group).
                    </div>
                </div>

                <div>
                    <div class="section-title">Education</div>
                    <div class="job-item" style="border:none; padding:0; margin-bottom: 10px;">
                        <div class="item-title">BSc Chemistry</div>
                        <div class="item-desc">University of Groningen</div>
                        <div class="item-desc" style="font-size: 11px; color:#64748b;">Sep 2021 - Aug 2025</div>
                        <div class="item-desc" style="font-style: italic; font-size: 11px;">Track: Chemistry of Life</div>
                    </div>
                </div>

                <div>
                    <div class="section-title">Awards</div>
                    <div class="job-item" style="border:none; padding:0; margin-bottom: 5px;">
                        <div class="item-title" style="font-size: 11.5px; font-weight: 400;"><a href="https://www.chess.com/news/view/2021-chesscom-awards-winners#member" style="color: #2563eb; text-decoration: none;">Chess.com Member of the Year 2021</a></div>
                    </div>
                    <div class="job-item" style="border:none; padding:0; margin-bottom: 10px;">
                        <div class="item-title" style="font-size: 11.5px; font-weight: 400;"><a href="https://harmonic.fun/news#blog-post-mathematician-sponsorships" style="color: #2563eb; text-decoration: none;">Harmonic Rising Mathematician (confidential)</a></div>
                    </div>
                </div>
            </div>

            <!-- MAIN CONTENT -->
            <div class="main-content">
                <div class="main-section">
                    <div class="main-title">About Me</div>
                    <div class="about-text">
                        Hi, I’m Tom! I graduated from the University of Groningen with a BSc in Chemistry. 
                        During this, I chose the Life Sciences track. I wrote my thesis in the Pollice Group, evaluating and optimizing NMR prediction with Graph Neural Networks.
                    </div>
                    <div class="about-text">
                        After graduation, I got more into math and programming. I wrote a program to automatically search jobs agentically, to no avail yet.
                        So, during my free time, I started to work on Project Euler (complex math challenges), which eventually led me to <strong>PNT+</strong>, an effort to create a human-readable proof of the Prime Number Theorem in Lean.
                    </div>
                    <div class="about-text">
                         Since my time at uni, I’ve developed myself to be a competent student mathematician and programmer.
                         So, without working experience in the field, I’m trying to make do with contributing to Open Source, and perform my hobbies in math, AI, and in the sciences.
                    </div>
                </div>

                <div class="main-section">
                    <div class="main-title">Skills</div>
                    <ul class="skills-ul skills-grid">
                        <li><strong>Math:</strong> Lean (Beginner), Formal Verification</li>
                        <li><strong>Code:</strong> Python (Medior), AI/ML (Medior)</li>
                        <li><strong>Science:</strong> Analytical (Bio)Chemistry</li>
                        <li><strong>Tools:</strong> Git, GitHub, VS Code, LaTeX</li>
                        <li><strong>Native:</strong> Dutch</li>
                        <li><strong>Fluent:</strong> English</li>
                    </ul>
                </div>

                <div class="main-section">
                    <div class="main-title">Featured Projects</div>
                    <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">PNT+ (Formal Verification)</span>
                        </div>
                        <p class="item-desc">
                            Formalizing complex number theory in Lean. Solving impactful theorems and lemmas.
                            <a href="https://github.com/AlexKontorovich/PrimeNumberTheoremAnd/issues?q=author%3Atomodovodoo%20OR%20reviewed-by%3Atomodovodoo" class="link-style">View Contributions</a>
                        </p>
                    </div>

                    <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">Automated Job Search Agent</span>
                        </div>
                        <p class="item-desc">
                            Developed a Python-based agentic tool to automate and optimize job searching workflows.
                        </p>
                    </div>
                    
                     <div class="project-item">
                        <div class="item-header">
                            <span class="item-title">Collection of Projects</span>
                        </div>
                        <p class="item-desc">
                           From Audio to Text from scratch, plotting immigration, vaccine, and water data, to manipulating single player savegame data, these are my University hobby projects.
                           <a href="https://github.com/Tomodovodoo/Collection-of-Projects" class="link-style">View on Github</a>
                        </p>
                    </div>
                </div>

                <div class="main-section">
                    <div class="main-title">Work & Community Experience</div>
                    
                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Transcom (for Odido)</span>
                            <span class="item-date">May 2024 - Nov 2024</span>
                        </div>
                        <p class="item-desc">Customer Service Representative. Consistent top performer in customer satisfaction.</p>
                    </div>

                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Teamspot</span>
                            <span class="item-date">Feb 2022 - July 2024</span>
                        </div>
                        <p class="item-desc">Regional Director (Northern Netherlands). Coordinated school projects and performed testing/data entry.</p>
                    </div>

                    <div class="job-item">
                        <div class="item-header">
                            <span class="item-title">Chess.com</span>
                            <span class="item-date">Jan 2022 - June 2022</span>
                        </div>
                        <p class="item-desc">Event Proctor & Moderator. Assisted in moderation of international online chess events and the "Leagues" project.</p>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Write HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"Generated {html_file}")

    # Find Browser (Edge is standard on Windows)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    browser_exe = None
    for path in edge_paths:
        if os.path.exists(path):
            browser_exe = path
            break
    
    if not browser_exe:
        print("Error: Could not find Microsoft Edge executable.")
        return

    # Generate PDF
    print(f"Generating PDF using {browser_exe}...")
    subprocess.run([
        browser_exe,
        "--headless",
        "--print-to-pdf=" + pdf_file,
        "--no-pdf-header-footer",
        html_file
    ], check=True, shell=True)
    
    # Post-process to ensure single page
    print("Post-processing PDF to strict 1-page limit...")
    try:
        reader = PdfReader(pdf_file)
        if len(reader.pages) > 1:
            print(f"PDF has {len(reader.pages)} pages. Trimming to 1 page...")
            writer = PdfWriter()
            writer.add_page(reader.pages[0])
            with open(pdf_file, "wb") as f:
                writer.write(f)
            print("Trimmed to single page.")
        else:
            print("PDF is already 1 page.")
    except Exception as e:
        print(f"Warning: Could not trim PDF: {e}")

    print(f"Generated {pdf_file}")

    # Generate Screenshot (PNG)
    # Dimensions for Sidebar layout: Keep consistent
    print(f"Generating PNG preview...")
    subprocess.run([
        browser_exe,
        "--headless",
        "--screenshot=" + png_file,
        "--window-size=794,1123", 
        "--force-device-scale-factor=2",
        html_file
    ], check=True, shell=True)
    print(f"Generated {png_file}")

if __name__ == "__main__":
    generate_cv()
