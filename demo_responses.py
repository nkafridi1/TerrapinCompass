"""
Demo-mode response engine.
Keyword-matches a user message against a curated bank of high-quality UMD-specific
responses and streams the result character-by-character so it feels like live AI.
"""

import time
import re
from typing import Generator

# ── Response bank ─────────────────────────────────────────────────────────────
# Each entry: (keywords_list, response_text)
# Keywords are matched case-insensitively; first match wins.

NAVIGATOR_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["first gen", "first-gen", "first generation", "nobody", "family never", "no one in my family"],
        """## You're in the right place — and UMD has your back.

Being first-gen is genuinely hard because no one hands you the manual. Here are the programs built specifically for students like you:

### 🌟 First-Gen Terp Initiative
UMD's dedicated community for first-generation students. Peer mentors who've already figured out the system, workshops on things like "how to email a professor" and "what advising actually does," and a network of faculty/staff allies.
- **Website:** firstgeneration.umd.edu

### 📚 TRIO Student Support Services (the big one)
Federally funded, free, and incredibly comprehensive — but most students never apply because they don't know it exists.
- **Who qualifies:** You only need ONE of: first-gen status, low-income background, OR documented disability
- **What you get:** Free tutoring, dedicated academic advisor, financial aid counseling, scholarship prep, cultural events
- **Website:** trio.umd.edu · **Email:** trio@umd.edu

### 🔬 McNair Scholars Program
If you're thinking about grad school at all, this is life-changing. Summer research stipend ($2,800), faculty mentor, full GRE prep, and hand-holding through every graduate school application.
- **Eligibility:** First-gen + low-income, OR underrepresented minority; min 2.8 GPA; junior/senior
- **Website:** mcnairscholars.umd.edu

### 🍎 Don't sleep on basic support either
- **Campus Pantry** (Stamp Student Union): free food, no questions asked
- **Emergency Fund:** one-time grants for unexpected hardship — financialaid.umd.edu/emergency-fund
- **Counseling Center "Let's Talk":** free 20-min drop-in chat with a counselor, no appointment needed

---

**Next Step:** Go to trio.umd.edu right now and start the application — it takes 20 minutes and could change your entire UMD experience."""
    ),
    (
        ["fafsa", "financial aid", "aid package", "grant", "federal aid", "fill out"],
        """## FAFSA — here's exactly what to know as a UMD student.

### When to file
File as early as **October 1** using the prior-prior year tax return (so for 2025–26, you use 2023 taxes). UMD's **priority deadline is February 15** — miss it and you lose access to limited state and institutional grants.

### What you'll likely receive (UMD-specific)
| Type | What it is | Has to be repaid? |
|------|-----------|-------------------|
| Federal Pell Grant | Up to $7,395/year for high-need students | ❌ No |
| UMD Need-Based Grant | Institutional money for high-need Terps | ❌ No |
| Maryland State Grant | For Maryland residents with financial need | ❌ No |
| Federal Work-Study | Part-time campus jobs (not automatic cash) | ❌ No |
| Direct Subsidized Loan | Interest-free while you're in school | ✅ Yes |
| Direct Unsubsidized Loan | Interest accrues immediately | ✅ Yes |

### Golden rule
Always accept grants first → work-study second → subsidized loans third → unsubsidized loans last. Never borrow more than you need.

### If your situation changed
Job loss, medical bills, divorce, death in the family — UMD's financial aid office (Lee Building, 301-314-9000) can do a **Professional Judgment review** to increase your aid based on current circumstances, not 2-year-old tax data. Most students don't know this option exists.

### Appeal your package
Got less than you expected? Write a respectful, specific appeal letter to sfa@umd.edu. Explain what changed and attach documentation. This works more often than people realize.

---

**Next Step:** Log in to studentaid.gov and check your FAFSA status today. If you haven't filed yet, do it this weekend — every week you wait costs you money."""
    ),
    (
        ["scholarship", "free money", "scholarship search", "money for school", "awards"],
        """## Scholarships you should be applying to right now.

Most students only apply to 2–3 scholarships. Students who get scholarships apply to 20+. Here's your UMD-specific hit list:

### 🏛️ UMD Scholarships
- **Banneker/Key Scholarship:** Full ride (tuition + room + board + fees + $1,000 enrichment). Maryland residents only; considered automatically during freshman admission. ~100 awarded per year. If you're still a student and didn't get it, ask OSFA about transfer/renewal opportunities.
- **Maryland Delegate/Senatorial Scholarship:** Up to full in-state tuition. Massively underused. You just email your state delegate or senator's office and ask. Most offices have unfilled slots.

### 🌍 Identity-Based (high-value, less competition)
- **Dream.US Scholarship** — Up to $33,000 for DACA/TPS recipients. UMD is a partner school. thedream.us
- **Gates Scholarship** — Full cost of attendance for high-achieving minority students with Pell eligibility. thegatesscholarship.org
- **UNCF Scholarships** — Multiple awards ($2,000–$10,000+) for Black students. uncf.org
- **CHCI Scholarship** — $2,500–$5,000 for Hispanic students. chci.org

### 🔄 Transfer Students
- **Jack Kent Cooke Undergraduate Transfer Scholarship:** Up to **$55,000/year**. For community college transfers with high GPA and financial need. One of the most valuable transfer scholarships in the US. jkcf.org

### 💡 Pro tips
1. Check **scholarships.umd.edu** — UMD lists dozens of department-specific awards most students ignore
2. Apply to local community foundation scholarships (your county, your high school's alumni foundation)
3. Small ($500–$2,000) scholarships have far less competition; 10 small ones = $5,000–$20,000
4. Reuse essays — one strong personal story can be adapted for 15 different applications

---

**Next Step:** Spend 20 minutes on scholarships.umd.edu and identify 5 you're eligible for. Then block 2 hours this weekend to write your first application."""
    ),
    (
        ["emergency", "food", "hungry", "can't pay", "broke", "eviction", "crisis", "afford", "money problem"],
        """## If you're in a tough spot right now, here's immediate help — no judgment.

### 🍎 Food — Campus Pantry
Free groceries and personal care items at the Stamp Student Union (near the loading dock). Walk in, take what you need. No application, no questions asked, no proof of income required.
- **Website:** campuspantry.umd.edu
- **Meal swipe donations:** Other students can donate dining swipes to the pantry — ask a staff member

### 💰 Emergency Financial Aid
UMD's Student Emergency Fund gives one-time grants for unexpected hardship:
- Medical bills, car repair (for commuters), sudden income loss, home emergency
- Apply at: financialaid.umd.edu/emergency-fund
- This is a **grant**, not a loan

### 🏠 Housing insecurity
Contact the Dean of Students Office (1130 Stamp, dos@umd.edu). They have protocols for students at risk of housing instability and can connect you with county resources.

### 🧠 Mental health — Right now
If you're in crisis: **301-314-7651** (Counseling Center, 24/7)
Not in crisis but overwhelmed: Walk into **Let's Talk** drop-in hours — no appointment, free 20-minute chat with a counselor. Check counseling.umd.edu for current times.

### 🚌 Transportation help
DOTS offers emergency ride assistance in some cases. The Shuttle-UM routes are free with your UMD ID and connect to the College Park Metro station.

---

**Next Step:** Go to the Campus Pantry today — even if you're "not sure you qualify." You do. It exists for exactly this situation."""
    ),
    (
        ["undocumented", "daca", "dreamer", "immigration", "international student", "visa", "iss", "f-1", "opt"],
        """## UMD has dedicated support for you — let's map it out.

### For Undocumented / DACA Students
**Dream.US Scholarship:** Up to $33,000 total for DACA and TPS recipients. UMD is an official partner. Apply at thedream.us — this is one of the largest scholarships specifically for Dreamers.

**Maryland Dream Act:** If you graduated from a Maryland high school and meet residency requirements, you may qualify for in-state tuition. Contact OSFA to confirm your eligibility.

**UMD Undocumented Student Support:** The Office of Diversity & Inclusion (diversity.umd.edu) has resources specifically for undocumented students, including legal referrals and community connections.

### For International Students (F-1, J-1, etc.)
**Office of International Students and Scholars (ISSS):**
- Location: 2101 Turner Hall
- Website: isss.umd.edu
- They handle CPT, OPT, visa renewals, travel signatures, and employment authorization
- Critical: Talk to ISSS *before* taking any job, changing enrollment status, or traveling internationally

**Scholarships open to international students:**
- Many UMD departmental scholarships are open to all students — check scholarships.umd.edu
- Some external scholarships (like Aga Khan Foundation, regional foundations) specifically fund international students

**Financial aid:** F-1 students are not eligible for federal aid, but UMD institutional scholarships and merit awards are available. Ask the OSFA specifically about options for international students.

### Community Support
- **MICA (Multicultural Involvement & Community Advocacy):** Stamp Student Union — community building for students of diverse backgrounds
- International Student Association and cultural organizations offer peer community

---

**Next Step:** Email isss@umd.edu (international students) or diversity@umd.edu (undocumented students) to schedule a 1:1 consultation. These offices exist to help you specifically."""
    ),
    (
        ["transfer", "transferred", "community college", "just transferred", "new to umd", "stars"],
        """## Welcome to UMD — transfer students have more resources than you think.

### 🌟 STARS — Your First Stop
Supporting Transfer and Returning Students (STARS) is built specifically for you.
- Transfer-specific orientation and transition workshops
- Peer connections with other transfer students
- Help figuring out how your credits apply and what's left to take
- **Website:** stars.umd.edu

### Credit Evaluation
Already happened, but if you have questions about how your credits transferred:
- See your departmental advisor AND the Transfer Credit Appeals office if anything seems wrong
- ARTSYS (artsys.usmd.edu) shows exactly how Maryland community college credits transfer — useful to know before taking future courses

### The Unwritten Rules Nobody Tells Transfer Students
1. **Register ASAP:** Transfer students often have late registration windows — being proactive about your schedule matters more than for freshmen
2. **Office hours exist and are free:** Go to professor office hours. Very few students do. It's how you get research opportunities, recommendation letters, and real mentorship.
3. **Your community college GPA still matters:** For grad school, employers often look at overall trajectory. Own your story.
4. **You can still get campus jobs:** Work-study, TA positions, research assistant roles — you're fully eligible

### Scholarships for Transfer Students
- **Jack Kent Cooke Transfer Scholarship:** Up to $55,000/year — the crown jewel for high-achieving transfers with financial need. jkcf.org
- **Maryland Delegate Scholarship:** Still applies — call your state delegate's office

---

**Next Step:** Visit stars.umd.edu and register for their next workshop or advising session. Then connect with one of their peer mentors — they've already navigated everything you're about to face."""
    ),
]

TUTOR_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["cmsc131", "cmsc 131", "java", "object oriented", "oop", "programming basics", "first cs class"],
        """## CMSC131 — Let's build your foundation right.

CMSC131 is where most CS careers begin. Java is the language, but **object-oriented thinking** is the real skill you're building.

### The core mental model
Everything in Java is an **object** — a bundle of data (fields) and behavior (methods). Think of a `Car` object: it has data (color, speed, fuel level) and behavior (accelerate, brake, refuel).

```java
public class Car {
    // Fields — the data the object holds
    private String color;
    private int speed;

    // Constructor — creates a new Car
    public Car(String color) {
        this.color = color;
        this.speed = 0;  // starts stopped
    }

    // Method — behavior the object can do
    public void accelerate(int amount) {
        speed += amount;
    }

    public int getSpeed() {
        return speed;
    }
}
```

### The three things students most get wrong in 131
1. **`this` keyword:** `this.color` means "the color field of *this specific object*." Without `this`, Java might look for a local variable named `color` instead.
2. **References vs. values:** When you assign one object to another (`Car b = a`), you're copying the *reference*, not the car. Both `a` and `b` now point to the same car.
3. **`null`:** An uninitialized reference. Calling a method on null crashes with `NullPointerException` — the most common 131 error.

### What are you specifically working on?
Tell me:
- Which project or assignment (Project 1 through 7)?
- What concept isn't clicking?
- Paste any code you're confused by

I'll walk you through it step by step.

**Also:** UMD's Learning Assistance Service (tutoring.umd.edu) has free drop-in tutoring for CMSC131. The CS TAs hold office hours in the Iribe Center — check the course schedule on ELMS for times."""
    ),
    (
        ["cmsc250", "discrete", "logic", "proof", "induction", "sets", "graphs", "propositional"],
        """## CMSC250 — Discrete Math demystified.

This course trips up a lot of students because it's the first CS course that's more math than programming. Here's the mindset shift: **you're learning the language that computer science is written in.**

### The Big 5 topics and how to think about them

**1. Propositional Logic**
Truth tables are mechanical — just evaluate every combination of T/F.
The tricky one: **implication (P → Q)** is only *false* when P is true and Q is false.
Memory trick: "If it rains, I'll carry an umbrella." This is only a lie if it rained and I didn't carry one.

**2. Predicate Logic (Quantifiers)**
- ∀x P(x) = "P is true for ALL x" — to disprove it, find ONE counterexample
- ∃x P(x) = "P is true for AT LEAST ONE x" — to prove it, find ONE example

**3. Proof Techniques**
| Technique | Use when |
|-----------|----------|
| Direct proof | You can get from hypothesis to conclusion in forward steps |
| Proof by contradiction | Assume the opposite, derive something impossible |
| Induction | Proving something for all natural numbers |
| Strong induction | Like induction, but you assume it's true for ALL values < n |

**4. Mathematical Induction (the one everyone struggles with)**
Template:
1. **Base case:** Show it's true for n=0 (or n=1)
2. **Inductive hypothesis:** *Assume* it's true for some arbitrary k
3. **Inductive step:** *Using that assumption*, prove it's true for k+1

The key insight: you're not proving it for k — you're proving "if it works for k, then it must work for k+1." Combined with the base case, this cascades to all n.

**5. Graph Theory**
Think of it visually. A graph is just dots (vertices) connected by lines (edges). Most proofs come down to counting edges and vertices carefully.

---

**What specific topic or homework problem is giving you trouble?** Paste it and I'll walk through it with you step by step."""
    ),
    (
        ["math140", "calc", "calculus", "derivative", "limit", "integral", "chain rule", "math 140"],
        """## MATH140 Calculus I — the key concepts that unlock everything else.

Calculus is fundamentally about two questions:
1. **How fast is something changing?** (derivatives)
2. **How much has accumulated?** (integrals)

### Limits — the foundation
A limit asks: *what value does f(x) approach as x gets close to a?*
It doesn't matter what f(a) actually equals — only what it *approaches*.

Common technique — when direct substitution gives 0/0, **factor and cancel:**
```
lim (x→2) of (x²-4)/(x-2)
= lim (x→2) of (x+2)(x-2)/(x-2)
= lim (x→2) of (x+2)
= 4
```

### Derivatives — the rate of change
The derivative f'(x) tells you the slope of f at any point x.

**Rules you must memorize cold:**
| Rule | Formula |
|------|---------|
| Power rule | d/dx [xⁿ] = nxⁿ⁻¹ |
| Chain rule | d/dx [f(g(x))] = f'(g(x)) · g'(x) |
| Product rule | d/dx [fg] = f'g + fg' |
| Quotient rule | d/dx [f/g] = (f'g - fg') / g² |

**Chain rule intuition:** You're differentiating the outside function, then multiplying by the derivative of what's inside.
Example: d/dx[sin(x²)] = cos(x²) · 2x

### What is giving you trouble?
- A specific type of problem (optimization, related rates, limits)?
- A specific homework question?
- The upcoming exam?

Tell me where you're stuck and I'll work through concrete examples with you.

**UMD resource:** The Math Success Program (math.umd.edu/undergraduate/resources) has drop-in tutoring for MATH140 in the Math Building. Highly recommended the week before exams."""
    ),
    (
        ["cmsc330", "ocaml", "functional", "lambda", "closure", "type system", "programming language"],
        """## CMSC330 — the course that changes how you think about code.

330 is hard because it attacks assumptions you built in 131/132. You're not just learning new syntax — you're learning different *paradigms* of computation.

### Functional Programming (OCaml section)
The core shift: **functions are values**. You can pass functions to functions, return them from functions, store them in variables.

```ocaml
(* A function that takes a function and applies it twice *)
let apply_twice f x = f (f x)

let double x = x * 2

let result = apply_twice double 3  (* = 12 *)
```

**Pattern matching** — OCaml's superpower:
```ocaml
let rec factorial n =
  match n with
  | 0 -> 1
  | n -> n * factorial (n - 1)
```
This is cleaner than if-else because the compiler warns you if you miss a case.

### Closures (the concept that trips everyone up)
A closure captures the environment where it was created:
```ocaml
let make_adder n =   (* n is "captured" *)
  fun x -> x + n     (* this function remembers n *)

let add5 = make_adder 5
let result = add5 10  (* = 15 *)
```

### Regular Expressions & CFGs
- Regex describes **regular languages** — patterns without memory
- Context-Free Grammars (CFGs) describe languages with **nested structure** (like parentheses or HTML)
- Key rule: If you need to "count" or "match" something, regex isn't enough — you need a CFG

### What part of 330 is giving you trouble?
The OCaml syntax? Closures? Type inference? CFG derivations? Regex? Tell me specifically and we'll work through it."""
    ),
    (
        ["bsci170", "biology", "ecology", "evolution", "genetics", "cell", "bsci", "chem135", "chemistry"],
        """## Let's tackle your bio/chem course — which topic specifically?

### BSCI170 — Ecology & Evolution
**The core evolutionary logic:**
Natural selection happens when three conditions are true:
1. There is **variation** in the trait
2. The trait is **heritable** (passed to offspring)
3. The trait affects **reproductive success**

That's it. Everything else (adaptation, speciation, arms races) follows from those three conditions.

**Ecology key relationships:**
- **Mutualism (+/+):** both species benefit (mycorrhizal fungi + plant roots)
- **Commensalism (+/0):** one benefits, other is unaffected
- **Parasitism (+/-):** one benefits at the other's expense
- **Predation (+/-):** similar to parasitism but kills immediately
- **Competition (-/-):** both are harmed

### CHEM135 — General Chemistry I
**Stoichiometry — the skill everything builds on:**
The mole (6.022 × 10²³ particles) is chemistry's "dozen" — it lets you count atoms by weighing them.

Strategy for stoichiometry problems:
1. Balance the equation
2. Convert given quantity → moles (using molar mass)
3. Use mole ratio from balanced equation
4. Convert moles → desired unit

**Limiting reagent:** The reactant that gets used up first, determining how much product forms. Find it by calculating how much product each reactant could make — the smaller answer is your limiting reagent.

---

**What specific concept or problem are you working through?** Paste it and I'll walk through the logic step by step. The more specific you are, the more useful I can be."""
    ),
    (
        ["stuck", "don't understand", "confused", "help me", "struggling", "failing", "hard", "test", "exam", "midterm"],
        """## Let's figure out exactly where you're stuck — then fix it.

First: feeling lost in a class at UMD is extremely normal. These courses are genuinely hard, and the students who succeed aren't smarter — they just got the right support faster.

**Tell me:**
1. Which course? (CMSC131, MATH140, BSCI170, something else?)
2. Which specific topic or assignment?
3. What do you understand so far? Walk me through it even if it feels incomplete.
4. What happens when you try to solve a problem — where do you get stuck?

Once I know the specifics, I'll:
- Identify the exact misconception (usually it's one specific thing)
- Walk through examples at your pace
- Show you the pattern so you can solve similar problems yourself

### Immediate UMD resources for your course:
- **Learning Assistance Service:** Free tutoring for most courses — tutoring.umd.edu
- **Writing Center:** For any writing-heavy course — writing.umd.edu
- **Professor office hours:** Every professor holds them; almost no students go. Go.
- **TA office hours:** Listed on ELMS under the course — often easier to get time with a TA
- **Supplemental Instruction (SI):** For gateway courses like CHEM135, MATH140, BSCI170 — free group study sessions with a trained SI leader

What are you working on? Let's get into it."""
    ),
]

CAREER_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["resume", "cv", "review my", "look at my", "improve my resume", "resume help"],
        """## Resume strategy for UMD students — especially non-traditional backgrounds.

### The core principle
Your resume is a marketing document, not a biography. Every line should answer: **"Why should they hire me?"**

### Structure (reverse chronological, 1 page as an undergrad)
```
YOUR NAME  |  email@umd.edu  |  LinkedIn  |  (optional) GitHub
─────────────────────────────────────────────────────────────
EDUCATION
University of Maryland, College Park            Expected May 2026
B.S. Computer Science | GPA: 3.4/4.0
Relevant coursework: CMSC330, CMSC351, STAT400

EXPERIENCE
Job Title, Company Name                         Month Year – Month Year
• [Action verb] [what you did] [measurable result]
• [Action verb] [what you did] [measurable result]

PROJECTS
Project Name                                    GitHub link (optional)
• Built [what] using [tech] that [result/impact]

SKILLS
Languages: Python, Java, C  |  Tools: Git, Linux  |  Frameworks: React
```

### Translating "non-traditional" experience
Many students discount their most impressive experiences. Here's how to reframe them:

| Your experience | How it reads on a resume |
|----------------|--------------------------|
| Worked 30 hrs/week while maintaining 3.5 GPA | Time management, prioritization under constraints |
| Cared for younger siblings/family members | Leadership, responsibility, project coordination |
| Food service / retail job | Customer communication, high-pressure performance, team coordination |
| Navigated college as a first-gen student | Resourcefulness, self-directed learning, problem-solving without a roadmap |
| Immigrant or multilingual background | Cross-cultural communication, adaptability |

**Never omit work experience** just because it wasn't "relevant." It shows work ethic.

### Bullet point formula
**[Strong action verb] + [specific task/project] + [quantifiable result]**
- ❌ "Helped customers with questions"
- ✅ "Resolved 50+ daily customer inquiries with 97% satisfaction rating"
- ❌ "Worked on a website project"
- ✅ "Built React dashboard that reduced report generation time from 4 hours to 15 minutes"

### UMD-specific
The **University Career Center** (careers.umd.edu) does free resume reviews — both walk-in and scheduled. Schedule one at least 3 weeks before any application deadline.

---

**Paste your resume** (or the sections you want reviewed) and I'll give you specific, line-by-line feedback with rewrites."""
    ),
    (
        ["interview", "behavioral", "tell me about yourself", "star method", "prepare", "mock interview"],
        """## Interview prep — especially for students who weren't taught this.

Most interview prep advice assumes you already know the unspoken rules. Let's lay them out.

### The STAR Method (your framework for every behavioral question)
**S**ituation → **T**ask → **A**ction → **R**esult

Every "tell me about a time when..." question gets answered with STAR. The key is that **A (Action)** should be 60% of your answer — that's what they care about.

**Example — "Tell me about a challenge you overcame"**

❌ Weak: "I had trouble in CMSC250 but I studied harder and passed."

✅ Strong: "In CMSC250, I was failing the midterm while working 25 hours a week. I identified that I was studying passively (re-reading notes), which wasn't working for proof-based math. I switched to writing out every proof from scratch, formed a study group with two classmates, and attended office hours twice a week. By the final, I'd gone from a 62 to an 89, and I learned that I absorb technical material through active recall, not passive review."

The second version shows self-awareness, problem-solving, and initiative — which is exactly what employers want.

### The 5 questions you WILL be asked
Prepare 2 stories for each:
1. "Tell me about yourself" (2-minute pitch: background → skills → why this role)
2. "Tell me about a challenge / failure" (growth, not victimhood)
3. "Tell me about working in a team" (your specific contribution)
4. "Why do you want to work here?" (do your research — 10 minutes on their website)
5. "Where do you see yourself in 5 years?" (be honest and ambitious; show direction)

### First-gen / non-traditional student superpower
You have stories most candidates don't. Navigating college without a roadmap, working while studying, supporting your family — these show resilience and real-world problem-solving. Own them.

### UMD Resources
- **University Career Center mock interviews:** Free, realistic, with written feedback — careers.umd.edu
- **Big Interview:** Free platform through UMD for recorded practice interviews
- **Terp Network:** Schedule an informational interview with a UMD alum in your target field

---

**Tell me the role you're interviewing for** and I'll give you tailored questions and sample answers."""
    ),
    (
        ["networking", "linkedin", "alumni", "connections", "no network", "don't know anyone", "reach out", "informational"],
        """## Networking without connections — the first-gen student's guide.

The word "networking" sounds transactional and gross. Reframe it: you're having **conversations with people who have done what you want to do.** That's it.

### The platform: Terp Network
400,000+ UMD alumni who signed up specifically to help current students. This is your unfair advantage.

**Step 1:** Go to terp.network and create a profile with your major, year, interests
**Step 2:** Search by industry, company, or role
**Step 3:** Send a message (template below)

### The outreach message that actually gets responses
```
Subject: UMD Terp — quick question about your path to [role/company]

Hi [Name],

I'm [Your name], a [year] [major] student at UMD. I came across your profile on Terp Network and was really interested in your work at [Company] doing [what they do].

I'm exploring careers in [field] and would love to hear about your path and any advice you'd give someone starting out. Would you be open to a 20-minute call or email exchange?

No worries if your schedule is tight — I really appreciate your time either way.

[Your name] | [Major] | Class of [year]
```

**Why this works:**
- Short, specific, low-pressure ("no worries if...")
- Shows you did homework (mentions their actual work)
- Asks for a *conversation*, not a job

### What to do in the informational interview
1. Start with: "How did you get to where you are now?"
2. Ask: "What do you wish you'd known starting out?"
3. Ask: "What's one thing that distinguishes candidates you'd hire?"
4. End with: "Is there anyone else you'd suggest I talk to?"

That last question is how your network grows. One conversation becomes five.

### LinkedIn fundamentals
- Your headline: `[Major] at University of Maryland | Interested in [field]`
- Include your UMD affiliation — alumni actively search for fellow Terps
- Post once: "Excited to be starting [internship/project]" — your UMD network will engage and expose you to recruiters

---

**What industry or company are you targeting?** I'll help you write a specific outreach message."""
    ),
    (
        ["internship", "job", "career fair", "recruiting", "apply", "summer", "entry level", "full time"],
        """## UMD job/internship strategy — timelines and tactics.

### Recruiting timelines (when to apply)
| Industry | When recruiting starts | For |
|---------|----------------------|-----|
| Big Tech (Google, Meta, Amazon) | **August–October** | Following summer internship |
| Finance / Consulting | **September–November** | Following summer internship |
| Government / Nonprofits | Rolling, many **December–March** deadlines | Summer and full-time |
| Healthcare / Research | Rolling; REU apps **January–February** | Summer research |
| Startups | Rolling year-round | — |

Most students apply in February for summer positions. **The students who get offers applied in September.**

### The UMD Career Fair (your biggest opportunity)
- **Fall Career Fair:** September in Stamp Student Union Grand Ballroom
- **Spring Career Fair:** February
- **STEM Career Fair:** Separate event in fall — bring your transcript and GitHub
- Free to attend with your UMD ID; hundreds of employers actively recruiting Terps

**Career fair tactics:**
1. Research 10 companies before you go — know their products and recent news
2. Wear business casual (not a suit, not jeans)
3. 30-second pitch: "I'm [name], studying [major]. I'm interested in [role] because [specific reason related to their work]. I've been working on [relevant project/course]."
4. Take the recruiter's card; email them that evening: "Great meeting you today..."

### Handshake — your #1 job platform
log in at umd.joinhandshake.com with your UMD credentials. Filter by "on-campus recruiting" to see employers coming to UMD specifically.

### The application math
Apply to 10× more than you think you need. A 5% callback rate on 40 applications = 2 interviews. A 5% rate on 5 applications = nothing. Cast wide, target deep on your top 5.

---

**What field are you targeting, and what year are you?** I'll give you a specific game plan."""
    ),
    (
        ["cover letter", "application", "writing a cover letter", "cover letter help"],
        """## Cover letters that get read — especially for non-traditional backgrounds.

Most cover letters are forgettable. Here's how to make yours stand out.

### The structure that works (4 paragraphs, 250–350 words)

**¶1 — The hook (2–3 sentences)**
Don't start with "I am writing to apply for..." Start with the reason you care.
> "When I helped my parents navigate their small business's finances with no formal training, I realized I had a knack for making complex financial information accessible — which is exactly what [Company]'s financial literacy platform does for millions of users."

**¶2 — Why you're qualified (3–4 sentences)**
Connect 2–3 specific experiences to the job requirements. Use the job description's own language.
> "In CMSC330 at UMD, I built a type inference engine in OCaml that taught me to reason about correctness under constraints — directly relevant to your compiler team's work..."

**¶3 — Why this company specifically (2–3 sentences)**
Show you did real research. Mention something specific about them — a product feature, a recent initiative, a value they've stated.

**¶4 — The close (1–2 sentences)**
Simple and confident. "I'd love to discuss how my background aligns with your team's goals. Thank you for your consideration."

### First-gen / non-traditional framing
Your path is your story. You don't need to hide the hardship — but frame it as *capability*, not struggle:
- ❌ "Despite coming from a low-income family and working 30 hours a week..."
- ✅ "Managing full-time coursework alongside 30 hours of work taught me to prioritize ruthlessly and deliver under pressure — skills I'll bring to..."

### One rule
Customize every cover letter. The template is the structure. The content — specific company name, specific job details, specific why — must be unique.

---

**Tell me the job description you're applying to** and I'll help you write a tailored first draft."""
    ),
]

FINANCIAL_RESPONSES: list[tuple[list[str], str]] = [
    (
        ["budget", "budgeting", "spending", "afford", "save money", "broke", "manage money", "financial plan"],
        """## Budgeting as a college student — practical, not preachy.

### The 50/30/20 framework (adapted for students)
Most budget advice is written for people with real income. Here's one that actually works for students:

| Category | % of income | What goes here |
|---------|------------|----------------|
| Needs | ~60–70% | Rent (if applicable), food, transportation, required course materials |
| Wants | ~10–20% | Eating out, entertainment, personal spending |
| Savings/Debt | ~10–20% | Emergency fund, paying extra on loans, savings goal |

If you're on a dining plan and living in the dorms, your "needs" are largely covered — what you're managing is your discretionary income.

### Build your first budget in 15 minutes
1. **List all income:** Financial aid disbursement, part-time job, family support, work-study
2. **List fixed expenses:** Phone bill, subscriptions, transit pass
3. **Estimate variable expenses:** Groceries, dining out, clothing — look at last month's bank statements
4. **What's left:** That's what you have for savings and variable wants

### Free tools
- **Monarch Money** or **YNAB** (You Need A Budget): app-based, designed for people with irregular income
- **Simple spreadsheet:** Income column, expense categories, subtract. Done.
- Your bank's built-in spending categories are usually enough to start

### UMD-specific money savers
- **Free printing:** 200 pages/semester through your UMD account
- **RecWell (Eppley):** Included in student fees — skip the gym membership
- **Shuttle-UM:** Free bus to Metro, Ikea, Target on some routes — check shuttle.umd.edu
- **Campus Pantry:** Free food — campuspantry.umd.edu — genuinely useful, not just for crises
- **Student discounts:** Spotify ($4.99/mo), Amazon Prime ($7.49/mo), Adobe Creative Cloud (~$20/mo), many restaurants near campus

### Emergency fund first
Before anything else: build a $500 emergency fund. One unexpected expense (car repair, medical bill, laptop dying) can cascade into credit card debt that takes years to clear. $500 blocks most small emergencies. Target $1,000 within a year.

---

**What's your specific situation?** Monthly income, biggest expenses, or a specific financial decision you're trying to make — I'll give you concrete numbers."""
    ),
    (
        ["loan", "student loan", "debt", "repayment", "subsidized", "unsubsidized", "interest", "borrow"],
        """## Student loans demystified — what they actually are and how to handle them.

### The two federal loan types (always prefer federal over private)
| | Subsidized | Unsubsidized |
|--|-----------|--------------|
| Interest while in school | Government pays it | **Accrues immediately** |
| Who qualifies | Demonstrated financial need | Anyone (undergrad) |
| Annual limit | Lower | Higher |
| Interest rate (2024-25) | 6.53% | 6.53% (same for undergrad) |

**Key insight:** If you have an unsubsidized loan at 6.53%, $10,000 accrues ~$653 in interest per year even while you're in school. That interest then capitalizes (gets added to principal) when repayment starts. Making even small payments during school ($25–50/month) saves meaningfully.

### Repayment plans — you have options
- **Standard:** 10-year repayment, fixed monthly payment, lowest total interest
- **Income-Driven Repayment (IDR):** Payment capped at 10% of discretionary income — good if you'll have a lower starting salary
- **SAVE Plan:** Newest IDR plan, most favorable terms — monthly payment can be $0 if your income is low enough
- **PSLF (Public Service Loan Forgiveness):** Work for a government or nonprofit for 10 years, make 120 payments — remaining balance forgiven. Potentially massive for public sector careers

### What to borrow
The rule of thumb: **borrow no more than your expected first-year salary.** If you're going into teaching ($45K), borrow no more than $45K total. If software engineering ($120K), more leverage makes sense.

### Never do this
- Don't take private loans if federal loans haven't been exhausted
- Don't borrow for living expenses beyond necessity
- Don't ignore your loan servicer — missed payments hurt your credit badly

### Check your loans right now
studentaid.gov — log in with your FSA ID to see every loan, balance, and servicer.

---

**How much have you borrowed so far, and what's your major/target career?** I'll run the numbers and tell you what your payments will actually look like."""
    ),
    (
        ["fafsa", "financial aid", "fill out", "css profile", "expected family", "efc", "aid"],
        """## FAFSA — the form that's worth thousands of dollars to get right.

### What FAFSA is (and why it matters)
The Free Application for Federal Student Aid determines your eligibility for:
- Federal grants (Pell Grant — up to $7,395/year, free money)
- Federal loans (lower interest rates than private)
- Federal Work-Study
- **Most state and institutional scholarships require it too** — including many UMD scholarships

### The most important thing: file EARLY
- **Opens:** October 1 each year (for the following academic year)
- **UMD priority deadline:** February 15 — after this, limited-fund grants may be exhausted
- **Use:** Prior-prior year taxes (e.g., 2026-27 FAFSA uses 2024 taxes)
- The IRS Data Retrieval Tool transfers your taxes automatically — use it

### How to maximize your aid
**1. Don't overreport assets.** Retirement accounts (401k, IRA) are NOT reported on FAFSA. Small business value has some exclusions. Primary home value is NOT reported.

**2. Submit before filing taxes if needed.** You can file with estimated numbers and correct later. Filing late costs you more than a minor correction.

**3. If your family's financial situation changed recently:** File a Special Circumstances Appeal with UMD's financial aid office. Job loss, medical bills, divorce — these can significantly increase your aid. Most students don't know this option exists.

**4. Dependency status:** If you're living independently, not receiving parental support, you may qualify as an "independent student," which changes your EFC dramatically. Ask OSFA.

### Common mistakes to avoid
- Listing a bank account balance from a high point in the year (measure it low)
- Forgetting to add UMD's school code (002103)
- Not completing the verification process if selected

### After you file
Check your myUMD portal at studentaid.gov and your UMD email weekly — missing documents hold up your disbursement.

---

**What part of the FAFSA process are you stuck on?** I'll walk you through it step by step."""
    ),
    (
        ["first paycheck", "paycheck", "taxes", "w-4", "401k", "benefits", "job offer", "starting salary"],
        """## Understanding your first real paycheck — everything they didn't teach you.

### Why your check is smaller than you expected
Let's say your offer is $60,000/year = $5,000/month gross. Here's where it goes:

| Deduction | ~Amount | What it is |
|----------|---------|-----------|
| Federal income tax | ~$500–700 | Depends on your W-4; gets reconciled at tax time |
| State income tax (MD: 4.75–5.75%) | ~$250–300 | Maryland has state + county tax |
| Social Security (6.2%) | ~$310 | Goes toward your future SS benefits |
| Medicare (1.45%) | ~$73 | Federal health insurance for 65+ |
| Health insurance premium | $50–200 | Depends on your plan election |
| 401(k) contribution | Your choice | Pre-tax savings for retirement |
| **Take-home (estimate):** | ~$3,400–3,700 | — |

### The W-4 form (fill this out at your first job)
The W-4 tells your employer how much federal tax to withhold. The new form is simpler — follow the instructions, and if you're single with one job, just fill out Step 1 and sign Step 5. No claiming "allowances" anymore.

### 401(k) — do this on day one
If your employer matches contributions (e.g., "we match 50% up to 6% of salary"), contribute **at least enough to get the full match.** An employer match is a 50–100% instant return on your money. Not contributing = leaving part of your salary on the table.

Even $100/month at 22, in a 401(k) earning 7% average returns, is ~$430,000 by age 65. Time is the asset.

### Health insurance — pick it at enrollment
During your benefits enrollment window (usually first 30 days, no exceptions), choose:
- **HDHP + HSA:** Lower premium, higher deductible. Best if you're young and healthy. The HSA is a tax-advantaged account for medical expenses.
- **PPO:** Higher premium, lower deductible. Better if you have ongoing prescriptions or conditions.
- **HMO:** Lowest premium, most restrictive network. Fine if you live where there are in-network providers.

### Your first tax return
File by **April 15**. Use FreeTaxUSA.com (free for federal) or IRS Free File if your income is under $79,000. You likely get a refund your first year if your withholding was too high — that's normal.

---

**Got a specific job offer or benefits package you want help decoding?** Paste the details and I'll walk through it with you."""
    ),
    (
        ["credit", "credit score", "credit card", "build credit", "credit history", "fico"],
        """## Building credit from zero — the right way.

### Why credit matters (and why to start now)
Your credit score affects: apartment applications, car loan rates, sometimes job offers, and eventually mortgage rates. Starting at 22 vs 27 is worth thousands in lower interest rates over your lifetime.

### How credit scores work (FICO)
| Factor | Weight | What it means |
|--------|--------|--------------|
| Payment history | 35% | Never miss a payment |
| Amounts owed | 30% | Keep utilization under 30% |
| Length of history | 15% | Older accounts = better |
| New credit | 10% | Don't open many accounts at once |
| Credit mix | 10% | Having different types helps |

**Most important rule: pay your full balance every month.** You build credit by showing you *can* borrow and pay back — not by carrying a balance. Carrying a balance just means you're paying 20-29% interest for no benefit.

### How to start with no credit
**Option 1 — Secured credit card**
You deposit $200–500 as collateral, which becomes your credit limit. Use it for small purchases ($30/month), pay it off in full. After 12–18 months, graduate to a regular card and get your deposit back.

**Option 2 — Become an authorized user**
Ask a family member with good credit to add you to their card. You don't need to use the card — their history shows up on your credit report.

**Option 3 — Credit-builder loan**
Some credit unions offer these specifically for students building credit.

### Cards good for students (no annual fee)
- **Discover it Student Chrome:** 2% cash back on gas/restaurants, 1% elsewhere
- **Capital One Quicksilver Student:** 1.5% cash back on everything
- **Petal 2:** Good for no-credit-history applicants

### Monitor your credit free
- **AnnualCreditReport.com:** Free official report from all 3 bureaus once/year
- **Credit Karma:** Free score tracking, no impact on score

---

**Where are you starting from?** No credit history, trying to improve a score, or dealing with a specific situation? I'll give you a concrete plan."""
    ),
]

# ── Default (fallback) responses per mode ─────────────────────────────────────

DEFAULTS = {
    "navigator": """## Let's find the right UMD resource for you.

I'm here to help you navigate UMD's ecosystem — especially resources that most students never hear about.

**Tell me more about what you're dealing with:**
- Financial situation (aid, scholarships, unexpected expenses)?
- First-gen or transfer student questions?
- A specific program or office you're trying to navigate?
- Emergency or urgent need?

The more specific you are, the better I can point you to exactly the right person, office, or program.

**Quick resource map:**
- 💰 Financial Aid: financialaid.umd.edu · Lee Building · 301-314-9000
- 🌟 First-Gen Programs: firstgeneration.umd.edu
- 📚 Free Tutoring: tutoring.umd.edu
- 🍎 Campus Pantry (free food): campuspantry.umd.edu
- 🧠 Counseling Center (24/7 crisis): 301-314-7651
- 💼 Career Center: careers.umd.edu · Hornbake Library""",

    "tutor": """## I'm ready to help you learn — what are we working on?

To give you the best help, tell me:
1. **Which course?** (CMSC131, MATH140, BSCI170, ENGL101, etc.)
2. **Which specific topic or assignment?**
3. **Where are you getting stuck?** Walk me through what you understand so far.

The more specific you are, the faster we can fix it. There's no such thing as a question too basic — every expert was once confused by the same thing.

**I can help with:**
- 🖥️ CS: CMSC131/132/216/250/330/351 — Java, C, algorithms, data structures
- 📐 Math: MATH140/141/240/241, STAT400
- 🧬 Bio/Chem: BSCI170/171/222, CHEM135/136
- ✍️ Writing: ENGL101, research papers, lab reports, grad school statements

**While you think:** UMD's Learning Assistance Service (tutoring.umd.edu) offers free drop-in tutoring for most gateway courses — great as a complement to what we work on here.""",

    "career": """## Let's work on your career — what's the specific goal?

I can help with:
- 📄 Resume review and rewriting (paste your current resume)
- 🎤 Interview prep (tell me the role)
- 🤝 Networking strategy (especially if you don't have connections yet)
- 📅 Timeline and strategy (internships, full-time, grad school)
- ✉️ Cover letters and outreach messages

**Quick wins right now:**
- Create a Handshake account at umd.joinhandshake.com
- Check when the next UMD Career Fair is at careers.umd.edu
- Look at the Terp Network (terp.network) — 400,000+ UMD alumni who want to help

**What specifically are you working on?** The more context you give me (target role, timeline, your background), the more targeted I can be.""",

    "financial": """## Let's talk money — what's your specific situation?

I can help with:
- 💳 Budgeting and managing student income
- 📋 Understanding your financial aid package
- 🏦 Student loans — types, repayment, what to borrow
- 💰 Saving strategies on a student budget
- 📊 Your first paycheck, taxes, and benefits
- 🏗️ Building credit from zero

**Tell me what you're dealing with:**
- A specific decision (should I take this loan? should I get this credit card?)
- A confusing document or form (FAFSA, loan paperwork, award letter)
- A general topic you want to understand better

No question is too basic. Many of these systems are deliberately confusing — asking is the smart move.

**UMD emergency resources:**
- Emergency Fund (one-time grants): financialaid.umd.edu/emergency-fund
- Campus Pantry (free food): campuspantry.umd.edu"""
}

# ── Matching logic ─────────────────────────────────────────────────────────────

def _score(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def get_demo_response(mode: str, user_message: str) -> str:
    banks = {
        "navigator": NAVIGATOR_RESPONSES,
        "tutor":     TUTOR_RESPONSES,
        "career":    CAREER_RESPONSES,
        "financial": FINANCIAL_RESPONSES,
    }
    bank = banks.get(mode, NAVIGATOR_RESPONSES)

    best_score = 0
    best_response = DEFAULTS.get(mode, DEFAULTS["navigator"])

    for keywords, response in bank:
        score = _score(user_message, keywords)
        if score > best_score:
            best_score = score
            best_response = response

    return best_response


def stream_demo_response(mode: str, user_message: str) -> Generator[str, None, None]:
    """Yield the demo response character by character to simulate streaming."""
    response = get_demo_response(mode, user_message)
    for char in response:
        yield char
        time.sleep(0.004)
