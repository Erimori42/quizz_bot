import os
import logging
import asyncio
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode
from dotenv import load_dotenv

# --- Setup ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Question Bank (Your 210 questions) ---
ALL_QUESTIONS = [
    # --- 70 Easy GMP Questions ---
    {"difficulty": "easy", "question": "What does 'GMP' primarily focus on?",
     "options": ["Marketing strategies", "Product quality and safety", "Employee salaries", "Office cleanliness"],
     "answer": "Product quality and safety",
     "explanation": "GMP (Good Manufacturing Practice) is a system to ensure products are consistently produced and controlled to quality standards.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'SOP'?",
     "options": ["Standard Office Procedure", "Standard Operating Protocol", "Standard Operating Procedure",
                 "Systematic Operational Plan"], "answer": "Standard Operating Procedure",
     "explanation": "An SOP provides detailed, written instructions to achieve uniformity of the performance of a specific function.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why is personal hygiene important in GMP?",
     "options": ["To look good for visitors", "To prevent product contamination", "It's a company tradition",
                 "To save on cleaning supplies"], "answer": "To prevent product contamination",
     "explanation": "Good personal hygiene practices by personnel help prevent contamination of the product.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What should be done with expired raw materials?",
     "options": ["Use them quickly", "Sell them at a discount", "Properly dispose of or reject them",
                 "Mix them with new materials"], "answer": "Properly dispose of or reject them",
     "explanation": "Expired materials may not meet quality standards and should not be used in manufacturing.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the purpose of a 'Batch Number' or 'Lot Number'?",
     "options": ["To count products", "For employee identification", "To uniquely identify a batch of product",
                 "For marketing purposes"], "answer": "To uniquely identify a batch of product",
     "explanation": "It allows for traceability throughout the manufacturing process and distribution.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What does 'Quarantine' mean for materials in GMP?",
     "options": ["Ready for use", "Rejected materials", "Held separately until quality tests are complete",
                 "Materials for sale"], "answer": "Held separately until quality tests are complete",
     "explanation": "Quarantined materials are isolated until they are tested and approved for use or rejected.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why must equipment be regularly cleaned?",
     "options": ["To make it look new", "To prevent cross-contamination and residue buildup", "Only if a manager asks",
                 "Once a year is enough"], "answer": "To prevent cross-contamination and residue buildup",
     "explanation": "Regular cleaning is essential to maintain product quality and prevent contamination.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Deviation' in GMP?",
     "options": ["A planned change", "An unexpected departure from approved procedures", "A lunch break",
                 "A marketing campaign"], "answer": "An unexpected departure from approved procedures",
     "explanation": "Deviations must be documented, investigated, and their impact assessed.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Who is responsible for following GMP guidelines in a manufacturing facility?",
     "options": ["Only managers", "Only quality assurance staff", "Every employee involved in manufacturing",
                 "Only new employees"], "answer": "Every employee involved in manufacturing",
     "explanation": "GMP is a collective responsibility involving everyone in the manufacturing process.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the importance of 'Training' in GMP?", "options": ["It's a formality",
                                                                                                   "To ensure personnel have the skills and knowledge to perform their jobs correctly",
                                                                                                   "Only for new hires",
                                                                                                   "To fill time"],
     "answer": "To ensure personnel have the skills and knowledge to perform their jobs correctly",
     "explanation": "Proper training is crucial for maintaining quality and compliance.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What should be recorded in a 'Logbook'?",
     "options": ["Personal notes", "Gossip about colleagues", "Activities related to equipment, rooms, or processes",
                 "Lunch orders"], "answer": "Activities related to equipment, rooms, or processes",
     "explanation": "Logbooks provide a chronological record of operations and events.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why are records important in GMP?",
     "options": ["To create more paperwork", "To provide evidence of compliance and traceability",
                 "To impress auditors", "They are not very important"],
     "answer": "To provide evidence of compliance and traceability",
     "explanation": "GMP relies heavily on accurate and complete records; 'if it wasn't documented, it didn't happen.'",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What does 'Calibration' mean for equipment?",
     "options": ["Cleaning the equipment", "Ensuring the equipment provides accurate readings",
                 "Painting the equipment", "Buying new equipment"],
     "answer": "Ensuring the equipment provides accurate readings",
     "explanation": "Calibration compares equipment readings to a known standard to ensure accuracy.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Cleanroom'?",
     "options": ["A room that is cleaned daily", "A room with controlled levels of contaminants",
                 "A storage room for cleaning supplies", "An office room"],
     "answer": "A room with controlled levels of contaminants",
     "explanation": "Cleanrooms are designed to minimize particulate and microbial contamination.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What should you do if you make a mistake in a GMP document?",
     "options": ["Use white-out to correct it", "Tear out the page",
                 "Cross it out with a single line, correct it, initial, and date it", "Ignore it"],
     "answer": "Cross it out with a single line, correct it, initial, and date it",
     "explanation": "This ensures the original entry is still legible and the correction is traceable.",
     "source": "Good Documentation Practices (GDP)"},
    {"difficulty": "easy", "question": "What is 'Cross-contamination'?",
     "options": ["Contamination from a different country",
                 "Contamination of a starting material or product with another material or product",
                 "Cleaning with a cross-shaped brush", "A type of approved contamination"],
     "answer": "Contamination of a starting material or product with another material or product",
     "explanation": "Preventing cross-contamination is a key objective of GMP.", "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the role of Quality Assurance (QA) in GMP?",
     "options": ["To perform all manufacturing steps", "To ensure that quality systems are in place and being followed",
                 "To sell the product", "To design the product packaging"],
     "answer": "To ensure that quality systems are in place and being followed",
     "explanation": "QA oversees the overall quality management system.", "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Validation' in GMP?", "options": ["A type of cleaning",
                                                                                   "Documented evidence that a process or system consistently does what it is supposed to do",
                                                                                   "Guessing the outcome",
                                                                                   "A marketing term"],
     "answer": "Documented evidence that a process or system consistently does what it is supposed to do",
     "explanation": "Validation provides a high degree of assurance for processes and systems.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What should be done with 'Rejected' materials?",
     "options": ["Use them anyway if you are careful", "Clearly identify and segregate them to prevent use",
                 "Hide them", "Repackage and sell them"],
     "answer": "Clearly identify and segregate them to prevent use",
     "explanation": "Rejected materials must be controlled to prevent their inadvertent use in manufacturing.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why is 'Traceability' important in GMP?",
     "options": ["It's a fun game", "To be able to track the history of a product or material",
                 "Only for expensive products", "It's not important"],
     "answer": "To be able to track the history of a product or material",
     "explanation": "Traceability is crucial for investigations, recalls, and ensuring product history is known.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Master Batch Record' (MBR)?",
     "options": ["A record of all master's degrees in the company",
                 "A recipe or set of instructions for manufacturing a specific product", "A list of all batches made",
                 "A record of cleaning activities"],
     "answer": "A recipe or set of instructions for manufacturing a specific product",
     "explanation": "The MBR contains all necessary information to produce a batch of a specific product.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Batch Manufacturing Record' (BMR)?",
     "options": ["The same as an MBR", "A record of the actual manufacturing steps and data for a specific batch",
                 "A marketing report for a batch", "A list of customer complaints for a batch"],
     "answer": "A record of the actual manufacturing steps and data for a specific batch",
     "explanation": "The BMR is completed during manufacturing and shows what actually happened.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the purpose of wearing gloves in a GMP area?",
     "options": ["To keep hands warm",
                 "To protect the product from contamination from hands, and sometimes to protect hands",
                 "Fashion statement", "Only if your hands are dirty"],
     "answer": "To protect the product from contamination from hands, and sometimes to protect hands",
     "explanation": "Gloves act as a barrier between personnel and the product or critical surfaces.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is an 'Audit' in the context of GMP?",
     "options": ["A financial check", "A systematic and independent examination to determine GMP compliance",
                 "A company party", "A performance review for an employee"],
     "answer": "A systematic and independent examination to determine GMP compliance",
     "explanation": "Audits help verify that GMP principles are being followed correctly.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What does 'Segregation' mean in GMP?", "options": ["Mixing everything together",
                                                                                           "Keeping different materials or products separate to prevent mix-ups or contamination",
                                                                                           "A type of company meeting",
                                                                                           "A cleaning chemical"],
     "answer": "Keeping different materials or products separate to prevent mix-ups or contamination",
     "explanation": "Proper segregation is key to preventing errors and contamination.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the 'Shelf Life' of a product?",
     "options": ["How long it sits on a shelf before being sold",
                 "The period during which a product is expected to remain within approved specifications",
                 "How long the packaging lasts", "The time it takes to manufacture the product"],
     "answer": "The period during which a product is expected to remain within approved specifications",
     "explanation": "Shelf life is determined by stability studies and indicates how long a product maintains its quality.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why is environmental monitoring important in cleanrooms?",
     "options": ["To check the weather", "To monitor and control microbial and particulate levels",
                 "To see if employees are comfortable", "It's not very important"],
     "answer": "To monitor and control microbial and particulate levels",
     "explanation": "Environmental monitoring ensures the cleanroom maintains its required level of cleanliness.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Recall'?", "options": ["Remembering something",
                                                                          "The process of retrieving a defective or potentially harmful product from the market",
                                                                          "A type of company holiday",
                                                                          "A new product launch"],
     "answer": "The process of retrieving a defective or potentially harmful product from the market",
     "explanation": "Recalls are initiated to protect public health.", "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What should be done before using a piece of equipment?",
     "options": ["Assume it's ready", "Check if it's clean, calibrated, and suitable for use",
                 "Start using it immediately", "Ask a colleague if it's okay"],
     "answer": "Check if it's clean, calibrated, and suitable for use",
     "explanation": "Pre-use checks are essential to ensure equipment operates correctly and doesn't compromise product quality.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Pest Control' in GMP?",
     "options": ["Keeping pets in the facility", "Measures to prevent and control pests like insects and rodents",
                 "A type of software", "A cleaning schedule"],
     "answer": "Measures to prevent and control pests like insects and rodents",
     "explanation": "Pests can be a source of contamination and must be controlled in a GMP facility.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the significance of 'Line Clearance'?",
     "options": ["Clearing a path for people to walk",
                 "Ensuring a production line is free of previous products/materials before starting a new batch",
                 "The end of the production line", "A type of employee break"],
     "answer": "Ensuring a production line is free of previous products/materials before starting a new batch",
     "explanation": "Line clearance prevents mix-ups and cross-contamination between different batches or products.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Data Integrity'?",
     "options": ["How strong your computer is", "The completeness, consistency, and accuracy of data",
                 "A type of data backup", "How fast data is processed"],
     "answer": "The completeness, consistency, and accuracy of data",
     "explanation": "Data integrity is crucial for making informed decisions and ensuring product quality.",
     "source": "Basic GMP Principles, ALCOA+"},
    {"difficulty": "easy", "question": "What is a 'Complaint' in GMP?",
     "options": ["An employee complaining about work",
                 "Any report from a customer or user about a product defect or issue", "A suggestion for improvement",
                 "A type of compliment"],
     "answer": "Any report from a customer or user about a product defect or issue",
     "explanation": "Complaints must be documented, investigated, and addressed.", "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the role of 'Management Review' in a quality system?",
     "options": ["Reviewing manager salaries",
                 "A formal evaluation by top management of the quality system's effectiveness", "A weekly team meeting",
                 "Reviewing marketing campaigns"],
     "answer": "A formal evaluation by top management of the quality system's effectiveness",
     "explanation": "Management review ensures the continued suitability and effectiveness of the quality system.",
     "source": "ICH Q10"},
    {"difficulty": "easy", "question": "What does 'Aseptic' mean?",
     "options": ["Very clean", "Free from disease-causing microorganisms", "A type of packaging",
                 "Related to aesthetics"], "answer": "Free from disease-causing microorganisms",
     "explanation": "Aseptic processing is used for sterile products to prevent microbial contamination.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "Why are 'Labels' important in GMP?",
     "options": ["For decoration", "To clearly identify materials, products, and equipment status", "Only for shipping",
                 "To use up extra paper"], "answer": "To clearly identify materials, products, and equipment status",
     "explanation": "Proper labeling prevents mix-ups and ensures correct use and identification.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Water for Injection' (WFI)?",
     "options": ["Any tap water", "Highly purified water used for manufacturing injectable products",
                 "Bottled mineral water", "Water used for cleaning"],
     "answer": "Highly purified water used for manufacturing injectable products",
     "explanation": "WFI must meet strict purity standards to be safe for parenteral use.",
     "source": "Pharmacopoeias (USP, EP)"},
    {"difficulty": "easy", "question": "What is 'Quality Control' (QC)?", "options": ["The same as Quality Assurance",
                                                                                      "The department responsible for testing materials and products against specifications",
                                                                                      "Controlling the number of products made",
                                                                                      "A customer service department"],
     "answer": "The department responsible for testing materials and products against specifications",
     "explanation": "QC performs testing to ensure products meet their quality standards before release.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Retained Sample'?",
     "options": ["A sample that was forgotten", "A sample of a batch of product kept for future reference or testing",
                 "A sample given to employees", "A rejected sample"],
     "answer": "A sample of a batch of product kept for future reference or testing",
     "explanation": "Retained samples are important for complaint investigations or re-testing if needed.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the basic principle of 'Risk Management' in GMP?",
     "options": ["Avoiding all risks", "Identifying, evaluating, and controlling potential risks to quality",
                 "Only for financial risks", "Ignoring minor risks"],
     "answer": "Identifying, evaluating, and controlling potential risks to quality",
     "explanation": "A risk-based approach helps focus efforts on what is most critical to product quality.",
     "source": "ICH Q9"},
    {"difficulty": "easy", "question": "What is the purpose of an 'Expiry Date' on a product?",
     "options": ["A suggestion for when to use it",
                 "The date after which the product should not be used as its quality may be compromised",
                 "The date it was manufactured", "A marketing trick"],
     "answer": "The date after which the product should not be used as its quality may be compromised",
     "explanation": "The expiry date is based on stability testing and ensures product safety and efficacy.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Sanitization' process?",
     "options": ["Making something look nice", "Reducing the number of microorganisms to a safe level",
                 "Sterilizing completely", "A type of mental exercise"],
     "answer": "Reducing the number of microorganisms to a safe level",
     "explanation": "Sanitization is a common cleaning step to control microbial contamination on surfaces.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Certificate of Analysis' (CoA)?",
     "options": ["A certificate for good analysis skills",
                 "A document confirming that a batch of material meets its specifications",
                 "A list of all possible analyses", "A financial report"],
     "answer": "A document confirming that a batch of material meets its specifications",
     "explanation": "A CoA provides test results and confirms the quality of a material or product.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Good Documentation Practice' (GDP)?",
     "options": ["Writing well", "Principles for ensuring data is accurate, legible, and traceable",
                 "A type of software", "Documenting only good results"],
     "answer": "Principles for ensuring data is accurate, legible, and traceable",
     "explanation": "GDP is essential for maintaining data integrity and reliable records.", "source": "WHO, ISPE"},
    {"difficulty": "easy", "question": "What is an 'Active Pharmaceutical Ingredient' (API)?",
     "options": ["Any ingredient in a drug", "The biologically active component of a drug product",
                 "A packaging material", "A cleaning agent"],
     "answer": "The biologically active component of a drug product",
     "explanation": "The API is the substance responsible for the therapeutic effect of the drug.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is an 'Excipient'?",
     "options": ["The main active drug", "An inactive substance formulated alongside the API", "A type of contaminant",
                 "A piece of equipment"], "answer": "An inactive substance formulated alongside the API",
     "explanation": "Excipients are used to help deliver the drug, improve stability, or aid manufacturing.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Process Flow' in manufacturing?",
     "options": ["How water flows in pipes", "The sequence of steps or operations in a manufacturing process",
                 "Employee movement in the facility", "A type of electrical current"],
     "answer": "The sequence of steps or operations in a manufacturing process",
     "explanation": "Understanding the process flow is important for process control and improvement.",
     "source": "Manufacturing Principles"},
    {"difficulty": "easy", "question": "Why is 'Temperature Control' important for some products?",
     "options": ["To make the room comfortable", "To maintain product stability and quality", "Only for hot products",
                 "It's not usually important"], "answer": "To maintain product stability and quality",
     "explanation": "Many pharmaceutical products are sensitive to temperature and require controlled storage and transport.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Material Safety Data Sheet' (MSDS) or 'Safety Data Sheet' (SDS)?",
     "options": ["A list of safe materials",
                 "A document providing information on the hazards and safe handling of a chemical", "A GMP procedure",
                 "A product advertisement"],
     "answer": "A document providing information on the hazards and safe handling of a chemical",
     "explanation": "SDS is crucial for worker safety when handling chemicals.",
     "source": "Occupational Safety Regulations"},
    {"difficulty": "easy", "question": "What does 'Yield' refer to in manufacturing?",
     "options": ["Giving way to traffic", "The amount of product obtained from a specific amount of starting material",
                 "Employee salary", "The speed of production"],
     "answer": "The amount of product obtained from a specific amount of starting material",
     "explanation": "Yield is a measure of process efficiency and is often monitored.",
     "source": "Manufacturing Principles"},
    {"difficulty": "easy", "question": "What is a 'Non-Conformance'?",
     "options": ["A type of uniform", "A failure to meet a specified requirement", "A successful outcome",
                 "A company policy"], "answer": "A failure to meet a specified requirement",
     "explanation": "Non-conformances must be investigated and addressed through the CAPA system.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the purpose of 'Air Locks' in a cleanroom facility?",
     "options": ["To lock the air inside",
                 "To maintain pressure differentials and prevent contaminant ingress between rooms of different cleanliness",
                 "A place to store air tanks", "A security feature to lock doors"],
     "answer": "To maintain pressure differentials and prevent contaminant ingress between rooms of different cleanliness",
     "explanation": "Air locks are critical for maintaining the integrity of cleanroom environments.",
     "source": "GMP Annex 1, ISO 14644"},
    {"difficulty": "easy", "question": "What does 'Approved Supplier' mean?",
     "options": ["Any supplier who is friendly",
                 "A supplier that has been evaluated and confirmed to meet quality requirements",
                 "The cheapest supplier", "A supplier located nearby"],
     "answer": "A supplier that has been evaluated and confirmed to meet quality requirements",
     "explanation": "Using approved suppliers is important for ensuring the quality of incoming materials.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Preventive Maintenance'?",
     "options": ["Maintenance done only after equipment breaks", "Scheduled maintenance to prevent equipment failures",
                 "Preventing employees from doing maintenance", "A type of cleaning"],
     "answer": "Scheduled maintenance to prevent equipment failures",
     "explanation": "Preventive maintenance helps ensure equipment reliability and reduces unplanned downtime.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Finished Product'?", "options": ["A product that is almost ready",
                                                                                    "A product that has completed all stages of manufacturing, including packaging",
                                                                                    "Raw materials",
                                                                                    "A product that has been sold"],
     "answer": "A product that has completed all stages of manufacturing, including packaging",
     "explanation": "The finished product is what is ultimately released for distribution and sale.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is the role of 'Sampling Plans' in QC?",
     "options": ["Plans for taking employee holidays",
                 "A defined procedure for taking a representative sample of material for testing",
                 "A map of the facility", "A list of all samples ever taken"],
     "answer": "A defined procedure for taking a representative sample of material for testing",
     "explanation": "Proper sampling is crucial to ensure that test results accurately reflect the quality of the entire batch.",
     "source": "Basic GMP Principles, Statistical Sampling Standards"},
    {"difficulty": "easy", "question": "What is 'Stability Testing'?", "options": ["Testing how stable an employee is",
                                                                                   "Testing a product over time under defined conditions to determine its shelf life",
                                                                                   "Testing the stability of a building",
                                                                                   "A quick test done once"],
     "answer": "Testing a product over time under defined conditions to determine its shelf life",
     "explanation": "Stability studies provide data to support the assigned expiry date of a product.",
     "source": "ICH Q1A"},
    {"difficulty": "easy", "question": "What is 'First-Pass Yield'?",
     "options": ["Yield after the first employee passes by",
                 "The percentage of units that complete a process and meet quality standards without rework",
                 "The yield of the first batch ever made", "A type of fishing yield"],
     "answer": "The percentage of units that complete a process and meet quality standards without rework",
     "explanation": "It's a common metric for process efficiency and quality.", "source": "Manufacturing Metrics"},
    {"difficulty": "easy", "question": "What is the primary goal of 'Good Housekeeping' in GMP?",
     "options": ["To make the facility look nice for auditors",
                 "To maintain a clean, tidy, and orderly environment to prevent contamination and accidents",
                 "A specific cleaning company", "A weekly deep clean only"],
     "answer": "To maintain a clean, tidy, and orderly environment to prevent contamination and accidents",
     "explanation": "Good housekeeping is a fundamental aspect of maintaining a GMP-compliant facility.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is a 'Controlled Document'?", "options": ["A document that is kept secret",
                                                                                       "A document that is managed under a formal system for issuance, revision, and distribution",
                                                                                       "Any document written on a computer",
                                                                                       "A document that is easy to control"],
     "answer": "A document that is managed under a formal system for issuance, revision, and distribution",
     "explanation": "Controlled documents (like SOPs, MBRs) ensure that only current, approved versions are in use.",
     "source": "Good Documentation Practices (GDP)"},
    {"difficulty": "easy", "question": "What does 'Work Order' typically mean in a maintenance context?",
     "options": ["An order to work harder", "A formal document authorizing and detailing specific maintenance tasks",
                 "A list of all work done in a day", "An employee's job description"],
     "answer": "A formal document authorizing and detailing specific maintenance tasks",
     "explanation": "Work orders help plan, track, and document maintenance activities.",
     "source": "Maintenance Management"},
    {"difficulty": "easy", "question": "What is an 'Investigation' in GMP often triggered by?",
     "options": ["Curiosity", "A deviation, OOS result, or complaint", "A new employee starting", "A successful batch"],
     "answer": "A deviation, OOS result, or complaint",
     "explanation": "Investigations aim to find the root cause of issues and implement corrective actions.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy",
     "question": "What is the purpose of 'Status Labeling' (e.g., 'Quarantine', 'Approved', 'Rejected')?",
     "options": ["To add color to the facility",
                 "To clearly indicate the current quality status of materials or equipment",
                 "A system for employee status", "Only used for new materials"],
     "answer": "To clearly indicate the current quality status of materials or equipment",
     "explanation": "Status labeling is crucial for preventing the use of incorrect or unapproved materials/equipment.",
     "source": "Basic GMP Principles"},
    {"difficulty": "easy", "question": "What is 'Annual Product Review' (APR) or 'Product Quality Review' (PQR)?",
     "options": ["A review of product marketing",
                 "A periodic review of a product's manufacturing and quality data to identify trends and areas for improvement",
                 "A customer satisfaction survey", "A review of the product's price"],
     "answer": "A periodic review of a product's manufacturing and quality data to identify trends and areas for improvement",
     "explanation": "APR/PQR helps ensure the consistency of the manufacturing process and the quality of the product.",
     "source": "FDA 21 CFR 211.180(e), EU GMP Chapter 1"},
    {"difficulty": "easy", "question": "What is 'Bioburden'?", "options": ["The weight of biological materials",
                                                                           "The number of microorganisms present on a surface or in a product before sterilization",
                                                                           "A type of cleaning agent",
                                                                           "A heavy burden for biologists"],
     "answer": "The number of microorganisms present on a surface or in a product before sterilization",
     "explanation": "Monitoring and controlling bioburden is critical, especially for sterile products.",
     "source": "Microbiology in GMP"},
    {"difficulty": "easy", "question": "What is the 'Design Qualification' (DQ) stage of validation?",
     "options": ["Qualifying the designer",
                 "Documented verification that the proposed design of facilities, systems, and equipment is suitable for the intended purpose",
                 "The final qualification step", "Designing a qualification plan"],
     "answer": "Documented verification that the proposed design of facilities, systems, and equipment is suitable for the intended purpose",
     "explanation": "DQ is typically the first step in the validation lifecycle for new systems/equipment.",
     "source": "GAMP 5, Validation Principles"},
    {"difficulty": "easy", "question": "What is 'Installation Qualification' (IQ)?",
     "options": ["Qualifying the installer",
                 "Documented verification that equipment or systems, as installed, comply with approved design and manufacturer's recommendations",
                 "Testing the equipment's operation", "Installing new software"],
     "answer": "Documented verification that equipment or systems, as installed, comply with approved design and manufacturer's recommendations",
     "explanation": "IQ confirms that the equipment is installed correctly and safely.",
     "source": "GAMP 5, Validation Principles"},
    {"difficulty": "easy", "question": "What is 'Operational Qualification' (OQ)?",
     "options": ["Qualifying the operator",
                 "Documented verification that equipment or systems operate as intended throughout anticipated operating ranges",
                 "The first qualification step", "Checking if the equipment is turned on"],
     "answer": "Documented verification that equipment or systems operate as intended throughout anticipated operating ranges",
     "explanation": "OQ tests the functionality of the equipment.", "source": "GAMP 5, Validation Principles"},
    {"difficulty": "easy", "question": "What is 'Performance Qualification' (PQ)?",
     "options": ["Reviewing employee performance",
                 "Documented verification that equipment or systems perform effectively and reproducibly based on the approved process method and specifications",
                 "The easiest qualification", "Checking if the equipment looks good"],
     "answer": "Documented verification that equipment or systems perform effectively and reproducibly based on the approved process method and specifications",
     "explanation": "PQ demonstrates that the equipment consistently produces quality product under normal operating conditions.",
     "source": "GAMP 5, Validation Principles"},

    # --- 70 Medium GMP Questions ---
    {"difficulty": "medium", "question": "What is the primary objective of a 'Change Control' system?",
     "options": ["To prevent all changes",
                 "To ensure changes are documented, evaluated, approved, and implemented in a controlled manner",
                 "To speed up changes", "To only document changes after they are made"],
     "answer": "To ensure changes are documented, evaluated, approved, and implemented in a controlled manner",
     "explanation": "A robust change control system prevents unintended consequences on product quality or validated systems.",
     "source": "ICH Q7, ICH Q10"},
    {"difficulty": "medium", "question": "What does 'ALCOA+' stand for in the context of data integrity?",
     "options": ["Accurate, Legible, Clear, Original, Attributable + Complete, Consistent, Enduring, Available",
                 "Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available",
                 "All Labs Must Comply, Otherwise Audit + Critical, Consistent, Enduring, Available",
                 "Authentic, Logical, Current, Official, Approved + Complete, Corroborated, Enduring, Accessible"],
     "answer": "Attributable, Legible, Contemporaneous, Original, Accurate + Complete, Consistent, Enduring, Available",
     "explanation": "ALCOA+ principles are fundamental to ensuring data integrity in GMP environments.",
     "source": "FDA Data Integrity Guidance, MHRA GxP Data Integrity Guidance"},
    {"difficulty": "medium", "question": "What is an 'Out of Specification' (OOS) result?",
     "options": ["A result that is better than expected",
                 "A test result that falls outside the established acceptance criteria or specifications",
                 "A result obtained using uncalibrated equipment", "Any result generated by the QC lab"],
     "answer": "A test result that falls outside the established acceptance criteria or specifications",
     "explanation": "OOS results require a thorough investigation to determine the cause and impact on the batch.",
     "source": "FDA Guidance for Industry - Investigating OOS Test Results"},
    {"difficulty": "medium", "question": "What is the main purpose of 'Process Validation'?",
     "options": ["To test the final product extensively",
                 "To establish documented evidence that a process will consistently produce a product meeting its pre-determined specifications and quality attributes",
                 "To train operators on a new process", "To reduce manufacturing costs"],
     "answer": "To establish documented evidence that a process will consistently produce a product meeting its pre-determined specifications and quality attributes",
     "explanation": "Process validation provides assurance that the manufacturing process is reliable and reproducible.",
     "source": "FDA Process Validation: General Principles and Practices"},
    {"difficulty": "medium",
     "question": "What is a 'Corrective Action and Preventive Action' (CAPA) system designed to do?",
     "options": ["Only punish employees for mistakes", "To collect customer feedback",
                 "To investigate deviations/non-conformances, identify root causes, implement corrective actions, and prevent recurrence",
                 "To manage company finances"],
     "answer": "To investigate deviations/non-conformances, identify root causes, implement corrective actions, and prevent recurrence",
     "explanation": "An effective CAPA system is a cornerstone of a GMP quality system and drives continuous improvement.",
     "source": "ICH Q10, FDA 21 CFR 820.100"},
    {"difficulty": "medium", "question": "What is the significance of 'Data Review' in a QC laboratory?",
     "options": ["A quick glance at the numbers",
                 "A thorough check of test data for accuracy, completeness, and compliance before results are approved",
                 "Only done if there is an OOS", "Performed by the person who generated the data only"],
     "answer": "A thorough check of test data for accuracy, completeness, and compliance before results are approved",
     "explanation": "Data review, often by a second person, is critical to ensure the reliability of QC results.",
     "source": "Laboratory Controls, GDP"},
    {"difficulty": "medium",
     "question": "What is meant by 'Worst-Case' conditions in validation studies (e.g., cleaning validation)?",
     "options": ["The easiest conditions to validate",
                 "Conditions that represent the most challenging scenario under which a process is still expected to work",
                 "Conditions that always cause failure", "Randomly selected conditions"],
     "answer": "Conditions that represent the most challenging scenario under which a process is still expected to work",
     "explanation": "Validating under worst-case conditions provides confidence that the process will be effective under normal operating ranges.",
     "source": "Validation Principles"},
    {"difficulty": "medium",
     "question": "What is the purpose of an 'Annual Product Review' (APR) or 'Product Quality Review' (PQR)?",
     "options": ["To decide if a product should be discontinued",
                 "To verify the consistency of the manufacturing process, assess trends, and identify potential improvements for a product",
                 "A marketing review of product sales", "A review of employee performance related to a product"],
     "answer": "To verify the consistency of the manufacturing process, assess trends, and identify potential improvements for a product",
     "explanation": "APR/PQR is a regulatory requirement and a tool for continuous improvement.",
     "source": "FDA 21 CFR 211.180(e), EU GMP Chapter 1"},
    {"difficulty": "medium", "question": "What is 'Qualification of Equipment'?",
     "options": ["Buying qualified equipment",
                 "A formal process of documented verification that equipment performs as intended and is suitable for its proposed use",
                 "Training employees on how to use equipment", "Cleaning equipment before use"],
     "answer": "A formal process of documented verification that equipment performs as intended and is suitable for its proposed use",
     "explanation": "Qualification typically involves DQ, IQ, OQ, and PQ stages.",
     "source": "GAMP 5, Validation Principles"},
    {"difficulty": "medium", "question": "What is the difference between 'Cleaning' and 'Sanitization'?",
     "options": ["They are the same thing",
                 "Cleaning removes visible dirt; sanitization reduces microorganisms to a safe level",
                 "Sanitization is only for food", "Cleaning is done with water, sanitization with chemicals"],
     "answer": "Cleaning removes visible dirt; sanitization reduces microorganisms to a safe level",
     "explanation": "Cleaning is usually a prerequisite for effective sanitization or disinfection.",
     "source": "GMP Cleaning Principles"},
    {"difficulty": "medium", "question": "What is a 'Stability Indicating Method' in analytical testing?",
     "options": ["A method that is very stable to perform",
                 "An analytical method that can accurately detect changes in the drug substance or drug product over time (e.g., degradation products)",
                 "A method used only for stability studies", "A quick and easy analytical method"],
     "answer": "An analytical method that can accurately detect changes in the drug substance or drug product over time (e.g., degradation products)",
     "explanation": "Such methods are crucial for accurately determining the shelf life of a product.",
     "source": "ICH Q1A, ICH Q2"},
    {"difficulty": "medium",
     "question": "What is the role of a 'Responsible Person' or 'Qualified Person' (QP) in EU GMP?",
     "options": ["The most responsible employee",
                 "A legally designated person responsible for certifying that each batch of medicinal product has been manufactured and tested in accordance with GMP and the marketing authorization",
                 "The head of manufacturing", "A quality control analyst"],
     "answer": "A legally designated person responsible for certifying that each batch of medicinal product has been manufactured and tested in accordance with GMP and the marketing authorization",
     "explanation": "The QP plays a critical role in the release of pharmaceutical products to the EU market.",
     "source": "EU GMP Annex 16"},
    {"difficulty": "medium", "question": "What is 'Technology Transfer' in pharmaceuticals?",
     "options": ["Transferring technology to another company for money",
                 "A documented process that transfers manufacturing processes and analytical methods from one site or scale to another (e.g., from R&D to production)",
                 "Upgrading computer systems", "Training on new software"],
     "answer": "A documented process that transfers manufacturing processes and analytical methods from one site or scale to another (e.g., from R&D to production)",
     "explanation": "Successful technology transfer ensures the receiving unit can consistently produce quality product.",
     "source": "ICH Q10, WHO TRS 961 Annex 7"},
    {"difficulty": "medium",
     "question": "What is the purpose of 'Environmental Monitoring' in aseptic processing areas?",
     "options": ["To check the outside weather",
                 "To regularly assess the microbiological and particulate quality of the manufacturing environment (air, surfaces, personnel)",
                 "To monitor employee comfort", "To save energy"],
     "answer": "To regularly assess the microbiological and particulate quality of the manufacturing environment (air, surfaces, personnel)",
     "explanation": "It provides an indication of the control over the aseptic environment.",
     "source": "GMP Annex 1, USP <1116>"},
    {"difficulty": "medium", "question": "What is a 'Master Validation Plan' (MVP)?",
     "options": ["A plan for validating all company masters degrees",
                 "A high-level document that describes the company's overall validation strategy, responsibilities, and the systems/processes to be validated",
                 "A list of all validation activities completed", "A plan for a single validation project"],
     "answer": "A high-level document that describes the company's overall validation strategy, responsibilities, and the systems/processes to be validated",
     "explanation": "The MVP provides a roadmap for the company's validation program.",
     "source": "Validation Principles"},
    {"difficulty": "medium", "question": "What is 'Mean Kinetic Temperature' (MKT)?",
     "options": ["The average temperature",
                 "A single calculated temperature at which the total amount of degradation over a particular period is equal to the sum of the individual degradations that would occur at various temperatures",
                 "The temperature of a moving object", "The highest temperature recorded"],
     "answer": "A single calculated temperature at which the total amount of degradation over a particular period is equal to the sum of the individual degradations that would occur at various temperatures",
     "explanation": "MKT is used to evaluate the impact of temperature excursions on product stability.",
     "source": "ICH Q1A, USP <1079>"},
    {"difficulty": "medium", "question": "What is the significance of 'Column Efficiency' in chromatography?",
     "options": ["How efficiently the column is packed",
                 "A measure of the column's ability to produce narrow peaks, indicating good separation",
                 "How long the column lasts", "The cost of the column"],
     "answer": "A measure of the column's ability to produce narrow peaks, indicating good separation",
     "explanation": "It's often expressed as the number of theoretical plates (N). Higher N means better efficiency.",
     "source": "Analytical Chemistry, Chromatography Principles"},
    {"difficulty": "medium",
     "question": "What is a 'Quality Agreement' between a contract manufacturer and a contract giver?",
     "options": ["An agreement to always provide high quality",
                 "A legally binding document that defines the specific GMP responsibilities of each party",
                 "An informal understanding", "A price list for quality services"],
     "answer": "A legally binding document that defines the specific GMP responsibilities of each party",
     "explanation": "Quality agreements are crucial for ensuring clarity and compliance in outsourced GMP activities.",
     "source": "ICH Q7, ICH Q10, FDA Contract Manufacturing Guidance"},
    {"difficulty": "medium", "question": "What is 'Aseptic Gowning Qualification'?",
     "options": ["Buying qualified gowns",
                 "A program to ensure personnel can consistently don sterile garments without compromising their sterility or the aseptic environment",
                 "A test of how fast personnel can gown", "A one-time training"],
     "answer": "A program to ensure personnel can consistently don sterile garments without compromising their sterility or the aseptic environment",
     "explanation": "It involves initial training, observation, and microbiological monitoring.",
     "source": "GMP Annex 1"},
    {"difficulty": "medium", "question": "What is the purpose of 'Smoke Studies' in cleanrooms?",
     "options": ["To test fire alarms",
                 "To visualize airflow patterns and verify that air is moving as designed (e.g., unidirectionally, away from critical areas)",
                 "To create a smoky atmosphere", "To check for leaks in the room"],
     "answer": "To visualize airflow patterns and verify that air is moving as designed (e.g., unidirectionally, away from critical areas)",
     "explanation": "Smoke studies help identify areas of turbulence or poor airflow that could pose a contamination risk.",
     "source": "GMP Annex 1, ISO 14644-3"},
    {"difficulty": "medium", "question": "What is 'Bracketing' in validation studies?",
     "options": ["Using brackets in documents",
                 "Validating only the extremes (e.g., smallest and largest sizes) of a range of similar products or equipment, assuming intermediate sizes are also covered",
                 "Putting items in brackets", "A type of statistical analysis"],
     "answer": "Validating only the extremes (e.g., smallest and largest sizes) of a range of similar products or equipment, assuming intermediate sizes are also covered",
     "explanation": "Bracketing can reduce validation effort but requires strong justification.",
     "source": "Validation Principles, ICH Q1D"},
    {"difficulty": "medium", "question": "What is 'Matrixing' in stability testing?",
     "options": ["A type of mathematical matrix",
                 "Testing only a subset of samples at specific time points, assuming stability of intermediate samples can be inferred",
                 "A type of data storage", "A complex experimental design"],
     "answer": "Testing only a subset of samples at specific time points, assuming stability of intermediate samples can be inferred",
     "explanation": "Matrixing can reduce the number of stability samples tested but needs careful design and justification.",
     "source": "ICH Q1A, ICH Q1D"},
    {"difficulty": "medium", "question": "What is a 'Reference Standard' in analytical testing?",
     "options": ["A standard textbook",
                 "A highly purified substance of known quality used as a benchmark for testing other samples",
                 "The first sample tested", "A standard operating procedure"],
     "answer": "A highly purified substance of known quality used as a benchmark for testing other samples",
     "explanation": "Reference standards are crucial for the accuracy and reliability of quantitative analytical results.",
     "source": "Pharmacopoeias (USP, EP), ICH Q7"},
    {"difficulty": "medium", "question": "What is 'Container Closure Integrity Testing' (CCIT)?",
     "options": ["Testing if a container can be closed",
                 "Evaluating the ability of a container closure system to maintain a sterile barrier and prevent leakage or contamination",
                 "Testing the strength of the container", "A visual inspection of the closure"],
     "answer": "Evaluating the ability of a container closure system to maintain a sterile barrier and prevent leakage or contamination",
     "explanation": "CCIT is critical for sterile products to ensure product sterility throughout its shelf life.",
     "source": "USP <1207>"},
    {"difficulty": "medium", "question": "What is the 'Limit of Detection' (LOD) of an analytical method?",
     "options": ["The limit of how much can be detected",
                 "The lowest amount of analyte in a sample that can be detected but not necessarily quantitated as an exact value",
                 "The highest amount that can be detected", "A limit set by the lab manager"],
     "answer": "The lowest amount of analyte in a sample that can be detected but not necessarily quantitated as an exact value",
     "explanation": "LOD indicates the sensitivity of an analytical method for detecting an analyte.",
     "source": "ICH Q2(R1)"},
    {"difficulty": "medium", "question": "What is the 'Limit of Quantitation' (LOQ) of an analytical method?",
     "options": ["The limit of how much can be quantified",
                 "The lowest amount of analyte in a sample that can be quantitatively determined with suitable precision and accuracy",
                 "The highest amount that can be quantified", "A limit for the number of samples"],
     "answer": "The lowest amount of analyte in a sample that can be quantitatively determined with suitable precision and accuracy",
     "explanation": "LOQ is important for methods used to measure low levels of analytes, such as impurities.",
     "source": "ICH Q2(R1)"},
    {"difficulty": "medium", "question": "What is 'Process Analytical Technology' (PAT)?",
     "options": ["Technology used by analysts",
                 "A system for designing, analyzing, and controlling manufacturing through timely measurements of critical quality and performance attributes of raw and in-process materials and processes",
                 "A specific analytical instrument", "A patent for an analytical process"],
     "answer": "A system for designing, analyzing, and controlling manufacturing through timely measurements of critical quality and performance attributes of raw and in-process materials and processes",
     "explanation": "PAT aims to build quality into the product by understanding and controlling the process in real-time or near real-time.",
     "source": "FDA PAT Guidance, ICH Q8"},
    {"difficulty": "medium", "question": "What is a 'Design Space' in the context of ICH Q8?",
     "options": ["The space where designers work",
                 "The multidimensional combination and interaction of input variables and process parameters that have been demonstrated to provide assurance of quality",
                 "A specific room in the facility", "A theoretical concept with no practical use"],
     "answer": "The multidimensional combination and interaction of input variables and process parameters that have been demonstrated to provide assurance of quality",
     "explanation": "Operating within the design space is not considered a change and provides operational flexibility.",
     "source": "ICH Q8 Pharmaceutical Development"},
    {"difficulty": "medium", "question": "What is 'Quality by Design' (QbD)?",
     "options": ["Designing high-quality products",
                 "A systematic approach to development that begins with predefined objectives and emphasizes product and process understanding and process control, based on sound science and quality risk management",
                 "A design review meeting", "A marketing strategy for quality products"],
     "answer": "A systematic approach to development that begins with predefined objectives and emphasizes product and process understanding and process control, based on sound science and quality risk management",
     "explanation": "QbD aims to build quality into the product from the design stage rather than testing it in.",
     "source": "ICH Q8, ICH Q9, ICH Q10"},
    {"difficulty": "medium", "question": "What is a 'Critical Process Parameter' (CPP)?",
     "options": ["A parameter that is critical to measure",
                 "A process parameter whose variability has an impact on a critical quality attribute (CQA) and therefore should be monitored or controlled to ensure the process produces the desired quality",
                 "The most difficult parameter to control", "A parameter that often fails"],
     "answer": "A process parameter whose variability has an impact on a critical quality attribute (CQA) and therefore should be monitored or controlled to ensure the process produces the desired quality",
     "explanation": "Identification and control of CPPs are key elements of QbD and process validation.",
     "source": "ICH Q8"},
    {"difficulty": "medium", "question": "What is a 'Critical Material Attribute' (CMA)?",
     "options": ["An attribute of a very important material",
                 "A physical, chemical, biological or microbiological property or characteristic of an input material that should be within an appropriate limit, range, or distribution to ensure the desired quality of output material",
                 "The cost of a material", "An attribute that is difficult to test"],
     "answer": "A physical, chemical, biological or microbiological property or characteristic of an input material that should be within an appropriate limit, range, or distribution to ensure the desired quality of output material",
     "explanation": "CMAs of starting materials and intermediates impact the CQAs of the final product.",
     "source": "ICH Q8"},
    {"difficulty": "medium", "question": "What is 'Real-Time Release Testing' (RTRT)?",
     "options": ["Testing products very quickly",
                 "The ability to evaluate and ensure the quality of in-process and/or final product based on process data, which typically include a valid combination of measured material attributes and process controls",
                 "Releasing products in real time as they are made", "A type of software for release"],
     "answer": "The ability to evaluate and ensure the quality of in-process and/or final product based on process data, which typically include a valid combination of measured material attributes and process controls",
     "explanation": "RTRT can reduce or eliminate end-product testing if the process is well understood and controlled.",
     "source": "ICH Q8, FDA PAT Guidance"},
    {"difficulty": "medium", "question": "What is a 'Biological Indicator' (BI) used for in sterilization validation?",
     "options": ["An indicator of biological activity in the room",
                 "A characterized preparation of specific microorganisms resistant to a particular sterilization process, used to demonstrate the effectiveness of that process",
                 "A type of plant used in labs", "An indicator that turns color when wet"],
     "answer": "A characterized preparation of specific microorganisms resistant to a particular sterilization process, used to demonstrate the effectiveness of that process",
     "explanation": "If the BIs are killed, it provides assurance that the sterilization process was effective.",
     "source": "USP <1229>, ISO 11138"},
    {"difficulty": "medium", "question": "What is a 'Chemical Indicator' (CI) used for in sterilization processes?",
     "options": ["An indicator of chemical spills",
                 "A system that reveals a change in one or more pre-defined process variables based on a chemical or physical change resulting from exposure to a process",
                 "A pH indicator", "An indicator that detects specific chemicals"],
     "answer": "A system that reveals a change in one or more pre-defined process variables based on a chemical or physical change resulting from exposure to a process",
     "explanation": "CIs provide a quick visual confirmation that items have been exposed to the sterilization process but do not prove sterility.",
     "source": "ISO 11140"},
    {"difficulty": "medium", "question": "What is 'Parametric Release'?",
     "options": ["Releasing products based on parameters set by marketing",
                 "A system of release that gives the assurance that the product is of the intended quality based on information collected during the manufacturing process and on the compliance with specific GMP requirements related to parametric release",
                 "Releasing only a parameter of the product", "A type of statistical release"],
     "answer": "A system of release that gives the assurance that the product is of the intended quality based on information collected during the manufacturing process and on the compliance with specific GMP requirements related to parametric release",
     "explanation": "Parametric release can replace certain end-product sterility tests if the sterilization process is robustly validated and monitored.",
     "source": "GMP Annex 17"},
    {"difficulty": "medium", "question": "What is a 'Pharmacopoeia' (e.g., USP, EP, JP)?",
     "options": ["A pharmacy encyclopedia",
                 "A legally binding collection of standards and quality specifications for medicines, excipients, and analytical methods",
                 "A history of pharmacy", "A journal for pharmacists"],
     "answer": "A legally binding collection of standards and quality specifications for medicines, excipients, and analytical methods",
     "explanation": "Compliance with pharmacopoeial standards is often a regulatory requirement.",
     "source": "General Knowledge"},
    {"difficulty": "medium",
     "question": "What is the purpose of 'Airflow Visualization Studies' (e.g., smoke studies)?",
     "options": ["To make the cleanroom look misty",
                 "To demonstrate that airflow patterns within a cleanroom or controlled environment are suitable to protect the product from contamination",
                 "To test the fire alarm system's smoke detectors", "To measure airflow speed only"],
     "answer": "To demonstrate that airflow patterns within a cleanroom or controlled environment are suitable to protect the product from contamination",
     "explanation": "These studies help identify and correct any undesirable airflow patterns that could compromise sterility or product quality.",
     "source": "EU GMP Annex 1, ISO 14644-3"},
    {"difficulty": "medium", "question": "What is 'Extractables and Leachables' testing primarily concerned with?",
     "options": ["Extracting active ingredients",
                 "Identifying and quantifying chemical compounds that migrate from container closure systems, processing equipment, or packaging into the drug product",
                 "Leaching color from the product", "Testing how much can be extracted from a plant"],
     "answer": "Identifying and quantifying chemical compounds that migrate from container closure systems, processing equipment, or packaging into the drug product",
     "explanation": "These compounds can pose a safety risk or affect product stability and efficacy.",
     "source": "PQRI Guidelines, USP <1663>, <1664>"},
    {"difficulty": "medium", "question": "What is a 'Validation Protocol'?",
     "options": ["A summary of validation results",
                 "A written plan stating how validation will be conducted, including test parameters, product characteristics, equipment, and acceptance criteria",
                 "A list of all validation SOPs", "A certificate issued after successful validation"],
     "answer": "A written plan stating how validation will be conducted, including test parameters, product characteristics, equipment, and acceptance criteria",
     "explanation": "The protocol must be approved before validation activities begin.",
     "source": "Validation Principles"},
    {"difficulty": "medium", "question": "What is a 'Validation Report'?",
     "options": ["A report on why validation is needed",
                 "A document that summarizes the results of validation activities, analyzes the data, and states whether the acceptance criteria were met",
                 "A daily report during validation", "A request to perform validation"],
     "answer": "A document that summarizes the results of validation activities, analyzes the data, and states whether the acceptance criteria were met",
     "explanation": "The validation report provides documented evidence of the validation outcome.",
     "source": "Validation Principles"},
    {"difficulty": "medium", "question": "What is 'Media Fill' in aseptic processing validation?",
     "options": ["Filling containers with social media content",
                 "A process simulation where a sterile microbiological growth medium is processed in the same way as the drug product to assess the sterility assurance of the process",
                 "Filling media bottles for the lab", "A type of food for microorganisms"],
     "answer": "A process simulation where a sterile microbiological growth medium is processed in the same way as the drug product to assess the sterility assurance of the process",
     "explanation": "If no growth occurs in the processed media units, it provides confidence in the aseptic process.",
     "source": "GMP Annex 1, FDA Aseptic Processing Guide"},
    {"difficulty": "medium", "question": "What is the 'Zone Concept' in cleanroom design (e.g., Grade A, B, C, D)?",
     "options": ["Different time zones for working",
                 "Defining areas of different cleanliness levels, with stricter controls in areas where the product is more exposed",
                 "Naming zones in the facility", "Zones for different types of equipment"],
     "answer": "Defining areas of different cleanliness levels, with stricter controls in areas where the product is more exposed",
     "explanation": "For example, Grade A (critical zone) is typically a localized environment for high-risk operations within a Grade B background.",
     "source": "EU GMP Annex 1"},
    {"difficulty": "medium", "question": "What is 'Unidirectional Airflow' (formerly Laminar Flow)?",
     "options": ["Air flowing in one random direction",
                 "An airflow moving in a single direction, in parallel paths, and at a constant velocity, sweeping particles away from critical areas",
                 "Air that flows in circles", "Air that is very slow"],
     "answer": "An airflow moving in a single direction, in parallel paths, and at a constant velocity, sweeping particles away from critical areas",
     "explanation": "Unidirectional airflow is critical for protecting exposed sterile products and surfaces in Grade A zones.",
     "source": "GMP Annex 1, ISO 14644"},
    {"difficulty": "medium", "question": "What is the purpose of 'Glove Integrity Testing' for isolators or RABS?",
     "options": ["To test if gloves fit well",
                 "To detect leaks or holes in gloves that could compromise the sterile barrier",
                 "To see how strong the glove material is", "A test performed only when new gloves are purchased"],
     "answer": "To detect leaks or holes in gloves that could compromise the sterile barrier",
     "explanation": "Regular glove integrity testing is crucial for maintaining the sterility of barrier systems.",
     "source": "GMP Annex 1, PDA TR No. 27"},
    {"difficulty": "medium", "question": "What is a 'Risk-Based Approach' to GMP?", "options": ["Ignoring all risks",
                                                                                                "Using scientific knowledge and experience to identify, analyze, evaluate, control, communicate, and review risks to product quality throughout the product lifecycle",
                                                                                                "Only focusing on high-risk products",
                                                                                                "A way to avoid GMP requirements"],
     "answer": "Using scientific knowledge and experience to identify, analyze, evaluate, control, communicate, and review risks to product quality throughout the product lifecycle",
     "explanation": "This approach allows resources to be focused on areas of higher risk to patient safety and product quality.",
     "source": "ICH Q9 Quality Risk Management"},
    {"difficulty": "medium", "question": "What is a 'Supplier Audit'?",
     "options": ["An audit of your company by a supplier",
                 "An audit conducted by a manufacturer at a supplier's facility to assess their quality systems and GMP compliance",
                 "A financial audit of a supplier", "An informal visit to a supplier"],
     "answer": "An audit conducted by a manufacturer at a supplier's facility to assess their quality systems and GMP compliance",
     "explanation": "Supplier audits are a key part of supplier qualification and ongoing monitoring.",
     "source": "Supplier Management, ICH Q10"},
    {"difficulty": "medium", "question": "What is 'Contamination Control Strategy' (CCS)?",
     "options": ["A strategy to control all company costs",
                 "A planned set of controls for microorganisms, pyrogens, and particulates, derived from current product and process understanding that assures process performance and product quality",
                 "A list of all contaminants", "A cleaning schedule"],
     "answer": "A planned set of controls for microorganisms, pyrogens, and particulates, derived from current product and process understanding that assures process performance and product quality",
     "explanation": "The CCS is a key concept in the revised EU GMP Annex 1, emphasizing a holistic approach to preventing contamination.",
     "source": "EU GMP Annex 1 (revised)"},
    {"difficulty": "medium", "question": "What is 'Water System Validation'?",
     "options": ["Validating the local water supply",
                 "Documented evidence that a pharmaceutical water system is designed, installed, operates, and performs consistently to produce water of the required quality",
                 "Testing tap water", "A one-time check of the water system"],
     "answer": "Documented evidence that a pharmaceutical water system is designed, installed, operates, and performs consistently to produce water of the required quality",
     "explanation": "This involves multiple phases of qualification and ongoing monitoring.",
     "source": "USP <1231>, EP Monograph for Purified Water/WFI"},
    {"difficulty": "medium", "question": "What is 'Computer System Validation' (CSV)?",
     "options": ["Validating all computers in the company",
                 "Documented evidence that a computerized system does what it purports to do, consistently and reliably, and is fit for its intended use",
                 "Installing antivirus software", "Training employees on how to use computers"],
     "answer": "Documented evidence that a computerized system does what it purports to do, consistently and reliably, and is fit for its intended use",
     "explanation": "CSV is critical for GMP-regulated computerized systems that impact product quality or data integrity.",
     "source": "GAMP 5, FDA 21 CFR Part 11"},
    {"difficulty": "medium", "question": "What is '21 CFR Part 11'?", "options": ["A chapter in a GMP textbook",
                                                                                  "A US FDA regulation that provides criteria for acceptance of electronic records, electronic signatures, and handwritten signatures executed to electronic records as equivalent to paper records and handwritten signatures executed on paper",
                                                                                  "A European regulation",
                                                                                  "A guideline for cleaning"],
     "answer": "A US FDA regulation that provides criteria for acceptance of electronic records, electronic signatures, and handwritten signatures executed to electronic records as equivalent to paper records and handwritten signatures executed on paper",
     "explanation": "It sets requirements for ensuring the trustworthiness and reliability of electronic records and signatures in GMP environments.",
     "source": "US FDA"},
    {"difficulty": "medium",
     "question": "What is a 'User Requirement Specification' (URS) in equipment/system qualification?",
     "options": ["A list of what users like",
                 "A document that specifies what the user wants the equipment or system to do, outlining the functional and operational needs",
                 "The equipment manual", "A purchase order for the equipment"],
     "answer": "A document that specifies what the user wants the equipment or system to do, outlining the functional and operational needs",
     "explanation": "The URS is a foundational document for designing and qualifying new equipment or systems.",
     "source": "GAMP 5"},
    {"difficulty": "medium", "question": "What is 'Traceability Matrix' in validation?",
     "options": ["A matrix for tracking employees",
                 "A document that traces requirements (e.g., from URS) through design, development, and testing to ensure all requirements are met and verified",
                 "A type of mathematical matrix", "A list of all traceable items"],
     "answer": "A document that traces requirements (e.g., from URS) through design, development, and testing to ensure all requirements are met and verified",
     "explanation": "It provides a clear link between what was required and what was delivered and tested.",
     "source": "Validation Principles, GAMP 5"},
    {"difficulty": "medium", "question": "What is 'Retrospective Validation'?",
     "options": ["Validating something you forgot to do",
                 "Validation of a process for a product already in distribution based upon accumulated production, testing, and control data",
                 "A less reliable form of validation", "Validating old equipment"],
     "answer": "Validation of a process for a product already in distribution based upon accumulated production, testing, and control data",
     "explanation": "Retrospective validation is generally discouraged and only acceptable in specific, justified circumstances when extensive historical data exists.",
     "source": "FDA Process Validation Guidance (historical context)"},
    {"difficulty": "medium", "question": "What is 'Concurrent Validation'?",
     "options": ["Validating two things at the same time",
                 "Validation carried out during routine production of product intended for sale",
                 "A quick validation method", "Validation performed by concurrent employees"],
     "answer": "Validation carried out during routine production of product intended for sale",
     "explanation": "Concurrent validation is used in specific circumstances, e.g., when product demand is high or batches are infrequent, and requires a robust protocol.",
     "source": "FDA Process Validation Guidance"},
    {"difficulty": "medium", "question": "What is 'Prospective Validation'?", "options": ["Validating future prospects",
                                                                                          "Validation conducted before the process is put into routine production or before product is distributed",
                                                                                          "A type of financial validation",
                                                                                          "The most expensive validation"],
     "answer": "Validation conducted before the process is put into routine production or before product is distributed",
     "explanation": "Prospective validation is the preferred and most common approach for new processes and products.",
     "source": "FDA Process Validation Guidance"},
    {"difficulty": "medium", "question": "What is 'GAMP 5'?", "options": ["A video game",
                                                                          "A Good Automated Manufacturing Practice guide for validation of automated systems in pharmaceutical manufacturing",
                                                                          "A type of GMP audit", "A government agency"],
     "answer": "A Good Automated Manufacturing Practice guide for validation of automated systems in pharmaceutical manufacturing",
     "explanation": "GAMP 5 provides a risk-based framework for validating computerized systems.",
     "source": "ISPE (International Society for Pharmaceutical Engineering)"},
    {"difficulty": "medium", "question": "What is 'ICH' and what is its primary role?",
     "options": ["International Cleaning House; sets cleaning standards",
                 "International Council for Harmonisation of Technical Requirements for Pharmaceuticals for Human Use; develops guidelines to ensure safe, effective, and high-quality medicines are developed and registered efficiently",
                 "Internal Company Handbook; employee guide",
                 "International Chemical Hazards; lists dangerous chemicals"],
     "answer": "International Council for Harmonisation of Technical Requirements for Pharmaceuticals for Human Use; develops guidelines to ensure safe, effective, and high-quality medicines are developed and registered efficiently",
     "explanation": "ICH guidelines are widely adopted by regulatory authorities globally.", "source": "ICH Website"},
    {"difficulty": "medium", "question": "What is the focus of ICH Q7?",
     "options": ["Quality Risk Management", "Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients",
                 "Pharmaceutical Development", "Pharmaceutical Quality System"],
     "answer": "Good Manufacturing Practice Guide for Active Pharmaceutical Ingredients",
     "explanation": "ICH Q7 provides detailed GMP guidance for the manufacturing of APIs.", "source": "ICH Q7"},
    {"difficulty": "medium", "question": "What is the focus of ICH Q9?",
     "options": ["Stability Testing", "Quality Risk Management", "Analytical Validation",
                 "Pharmaceutical Quality System"], "answer": "Quality Risk Management",
     "explanation": "ICH Q9 provides principles and examples of tools for quality risk management that can be applied to different aspects of pharmaceutical quality.",
     "source": "ICH Q9"},
    {"difficulty": "medium", "question": "What is the focus of ICH Q10?",
     "options": ["Good Manufacturing Practice for APIs", "Pharmaceutical Quality System",
                 "Impurities in New Drug Substances", "Validation of Analytical Procedures"],
     "answer": "Pharmaceutical Quality System",
     "explanation": "ICH Q10 describes a model for an effective pharmaceutical quality system that applies throughout the product lifecycle.",
     "source": "ICH Q10"},
    {"difficulty": "medium", "question": "What is a 'Type I Water' according to USP/EP specifications?",
     "options": ["Tap water",
                 "The highest grade of purified water, typically used for critical analytical applications",
                 "Water for Injection", "Water for cleaning"],
     "answer": "The highest grade of purified water, typically used for critical analytical applications",
     "explanation": "Type I water has very low levels of ionic, organic, and particulate contaminants.",
     "source": "USP <1231>, EP monograph for Purified Water"},
    {"difficulty": "medium", "question": "What is 'Endotoxin' (or Lipopolysaccharide - LPS)?",
     "options": ["A toxin found only on the ends of bacteria",
                 "A component of the outer membrane of Gram-negative bacteria that can cause fever and other adverse reactions if present in injectable drug products",
                 "A type of cleaning agent", "A beneficial bacteria"],
     "answer": "A component of the outer membrane of Gram-negative bacteria that can cause fever and other adverse reactions if present in injectable drug products",
     "explanation": "Control and testing for endotoxins (pyrogens) are critical for parenteral drugs.",
     "source": "Microbiology, USP <85> Bacterial Endotoxins Test"},
    {"difficulty": "medium", "question": "What is the 'LAL Test' (Limulus Amebocyte Lysate Test)?",
     "options": ["A test for laughing gas",
                 "An in vitro assay used for the detection and quantification of bacterial endotoxins",
                 "A test for animal allergies", "A type of liver function test"],
     "answer": "An in vitro assay used for the detection and quantification of bacterial endotoxins",
     "explanation": "The LAL test is a widely used method for endotoxin testing in the pharmaceutical industry.",
     "source": "USP <85>"},
    {"difficulty": "medium", "question": "What is 'Depyrogenation'?", "options": ["Making someone less angry",
                                                                                  "A process used to remove or inactivate pyrogens (primarily endotoxins) from materials or equipment",
                                                                                  "A type of fire extinguishing method",
                                                                                  "Cooling down a product"],
     "answer": "A process used to remove or inactivate pyrogens (primarily endotoxins) from materials or equipment",
     "explanation": "Common methods include dry heat (for glassware) or ultrafiltration (for solutions).",
     "source": "Sterilization & Aseptic Processing"},
    {"difficulty": "medium", "question": "What is a 'Material Review Board' (MRB)?",
     "options": ["A board that reviews new materials for purchase",
                 "A cross-functional team responsible for reviewing and making decisions on non-conforming materials or products",
                 "A group of material suppliers", "A library for materials"],
     "answer": "A cross-functional team responsible for reviewing and making decisions on non-conforming materials or products",
     "explanation": "The MRB decides whether non-conforming material can be reworked, used-as-is (with justification), or must be rejected.",
     "source": "Quality Management Systems"},
    {"difficulty": "medium", "question": "What is 'Clean Hold Time' in cleaning validation?",
     "options": ["How long it takes to clean",
                 "The maximum time equipment can be held in a clean state before it needs to be re-cleaned or used",
                 "The time equipment is held for cleaning", "A type of cleaning chemical"],
     "answer": "The maximum time equipment can be held in a clean state before it needs to be re-cleaned or used",
     "explanation": "This study ensures that equipment does not become re-contaminated during storage after cleaning.",
     "source": "Cleaning Validation Principles"},
    {"difficulty": "medium", "question": "What is 'Dirty Hold Time' in cleaning validation?",
     "options": ["How long equipment stays dirty",
                 "The maximum time equipment can be held in a dirty state after use and before cleaning, without adversely affecting the cleaning process effectiveness",
                 "The time it takes for dirt to appear", "A measure of how dirty equipment is"],
     "answer": "The maximum time equipment can be held in a dirty state after use and before cleaning, without adversely affecting the cleaning process effectiveness",
     "explanation": "This study ensures that residues do not become more difficult to clean over time.",
     "source": "Cleaning Validation Principles"},

    # --- 70 Hard GMP Questions ---
    {"difficulty": "hard",
     "question": "In the context of ICH Q9 (Quality Risk Management), what is the primary difference between 'risk assessment' and 'risk control'?",
     "options": ["Assessment identifies hazards, control eliminates them",
                 "Assessment is qualitative, control is quantitative",
                 "Assessment involves identification, analysis, and evaluation of risk; control involves reducing or accepting risks",
                 "Assessment is done by QA, control by production"],
     "answer": "Assessment involves identification, analysis, and evaluation of risk; control involves reducing or accepting risks",
     "explanation": "Risk assessment is the overall process of risk identification, analysis, and evaluation. Risk control focuses on decision-making to reduce and/or accept risks.",
     "source": "ICH Q9 Quality Risk Management"},
    {"difficulty": "hard",
     "question": "What is the primary purpose of a 'Continued Process Verification' (CPV) program as outlined in FDA's Process Validation guidance (Stage 3)?",
     "options": ["To revalidate the entire process annually",
                 "An ongoing program to collect and analyze process data to ensure the process remains in a state of control during routine commercial manufacture",
                 "To validate only new products", "To replace annual product reviews"],
     "answer": "An ongoing program to collect and analyze process data to ensure the process remains in a state of control during routine commercial manufacture",
     "explanation": "CPV (Stage 3) ensures that the process remains in a validated state throughout its lifecycle by continually monitoring process parameters and quality attributes.",
     "source": "FDA Process Validation Guidance (Stage 3)"},
    {"difficulty": "hard",
     "question": "According to EU GMP Annex 1 (Manufacture of Sterile Medicinal Products), what is the maximum permitted number of particles ≥0.5 µm/m³ for a Grade A environment 'at rest'?",
     "options": ["3,520", "352,000", "20", "29"], "answer": "3,520",
     "explanation": "For Grade A 'at rest', the limit for particles ≥0.5 µm/m³ is 3,520. The limit for ≥5.0 µm/m³ is 29 (revised Annex 1, 2022).",
     "source": "EU GMP Annex 1 (2022 Revision)"},
    {"difficulty": "hard",
     "question": "What is a key consideration when validating a 'Sterilizing Grade Filter' as per PDA Technical Report No. 26?",
     "options": ["Its color change after use",
                 "Bacterial challenge testing using Brevundimonas diminuta (ATCC 19146) at a minimum challenge of 10⁷ CFU/cm² of filter surface area",
                 "The filter's price", "How quickly it filters"],
     "answer": "Bacterial challenge testing using Brevundimonas diminuta (ATCC 19146) at a minimum challenge of 10⁷ CFU/cm² of filter surface area",
     "explanation": "This specific organism and challenge level are standard for demonstrating the sterilizing capability of a 0.22 µm (or 0.2 µm) rated filter.",
     "source": "PDA Technical Report No. 26 (Revised 2008) - Sterilizing Filtration of Liquids"},
    {"difficulty": "hard",
     "question": "In the context of ICH Q3D for elemental impurities, what is a 'Permitted Daily Exposure' (PDE)?",
     "options": ["The maximum amount of an element permitted in a daily dose of a drug product",
                 "The daily exposure limit for workers handling the element",
                 "The amount of an element that causes a detectable effect",
                 "A guideline for environmental discharge of the element"],
     "answer": "The maximum amount of an element permitted in a daily dose of a drug product",
     "explanation": "PDE values are established based on toxicological data and represent a dose that is unlikely to cause an appreciable risk to human health during a lifetime of exposure.",
     "source": "ICH Q3D Guideline for Elemental Impurities"},
    {"difficulty": "hard",
     "question": "What is the primary goal of 'Pharmaceutical Development' as described in ICH Q8(R2)?",
     "options": ["To develop the cheapest manufacturing process",
                 "To design a quality product and its manufacturing process to consistently deliver the intended performance of the product",
                 "To complete development as quickly as possible", "To find as many new uses for a drug as possible"],
     "answer": "To design a quality product and its manufacturing process to consistently deliver the intended performance of the product",
     "explanation": "ICH Q8(R2) emphasizes a systematic, science and risk-based approach to pharmaceutical development, including the concept of Quality by Design (QbD).",
     "source": "ICH Q8(R2) Pharmaceutical Development"},
    {"difficulty": "hard",
     "question": "What does the term 'Lifecycle Approach' to process validation, as described by the FDA, entail?",
     "options": ["Validating a process only once in its lifecycle",
                 "An integrated approach linking product and process development, qualification of the commercial manufacturing process, and maintenance of the process in a state of control during routine production",
                 "The lifecycle of the validation documents", "Focusing on the end-of-life disposal of the product"],
     "answer": "An integrated approach linking product and process development, qualification of the commercial manufacturing process, and maintenance of the process in a state of control during routine production",
     "explanation": "This approach consists of three stages: Process Design (Stage 1), Process Qualification (Stage 2), and Continued Process Verification (Stage 3).",
     "source": "FDA Process Validation: General Principles and Practices (2011)"},
    {"difficulty": "hard", "question": "According to GAMP 5, what is a 'Category 4' software system?",
     "options": ["Operating systems", "Standard software packages (non-configurable)",
                 "Configured software products (e.g., LIMS, ERP configured for GMP use)", "Custom bespoke software"],
     "answer": "Configured software products (e.g., LIMS, ERP configured for GMP use)",
     "explanation": "GAMP 5 categorizes software to guide the validation effort. Category 4 systems are configured off-the-shelf products requiring significant configuration to meet business needs.",
     "source": "ISPE GAMP 5: A Risk-Based Approach to Compliant GxP Computerized Systems"},
    {"difficulty": "hard", "question": "What is the 'D-value' in sterilization validation?",
     "options": ["The design value of the sterilizer",
                 "The time (or dose) required at a given condition (e.g., temperature) to achieve a 1-log (90%) reduction in the population of a specific microorganism",
                 "The duration of the sterilization cycle", "The depth of a dent in a can after sterilization"],
     "answer": "The time (or dose) required at a given condition (e.g., temperature) to achieve a 1-log (90%) reduction in the population of a specific microorganism",
     "explanation": "D-value is a measure of a microorganism's resistance to a specific sterilization process.",
     "source": "Sterilization Principles, USP <1229>"},
    {"difficulty": "hard", "question": "What is the 'Z-value' in thermal sterilization validation?",
     "options": ["The final value of the process",
                 "The temperature change required to achieve a 1-log change in the D-value",
                 "The zone of the sterilizer with the lowest temperature", "A type of statistical value"],
     "answer": "The temperature change required to achieve a 1-log change in the D-value",
     "explanation": "Z-value characterizes the temperature dependence of the microbial inactivation rate.",
     "source": "Sterilization Principles, USP <1229>"},
    {"difficulty": "hard", "question": "What is a 'Type I Error' (alpha error) in statistical process control?",
     "options": ["Accepting a bad batch", "Rejecting a good batch (producer's risk)",
                 "Failing to detect a process shift", "Using the wrong statistical test"],
     "answer": "Rejecting a good batch (producer's risk)",
     "explanation": "A Type I error occurs when a process that is actually in control is incorrectly judged to be out of control, leading to unnecessary action.",
     "source": "Statistical Process Control (SPC) Principles"},
    {"difficulty": "hard", "question": "What is a 'Type II Error' (beta error) in statistical process control?",
     "options": ["Rejecting a good batch", "Accepting a bad batch (consumer's risk)", "Making a calculation mistake",
                 "A very serious error"], "answer": "Accepting a bad batch (consumer's risk)",
     "explanation": "A Type II error occurs when a process that is actually out of control is incorrectly judged to be in control, potentially leading to the release of non-conforming product.",
     "source": "Statistical Process Control (SPC) Principles"},
    {"difficulty": "hard", "question": "What is the primary purpose of 'Adverse Event Reporting' in pharmacovigilance?",
     "options": ["To blame the drug manufacturer",
                 "To identify potential safety signals and contribute to the overall safety profile of a medicinal product",
                 "To get compensation for patients", "To stop the sale of all drugs"],
     "answer": "To identify potential safety signals and contribute to the overall safety profile of a medicinal product",
     "explanation": "Systematic collection and analysis of adverse event reports are crucial for post-marketing surveillance and patient safety.",
     "source": "ICH E2A, E2D"},
    {"difficulty": "hard", "question": "In cleaning validation, what does 'Visually Clean' mean?",
     "options": ["The equipment looks shiny",
                 "The absence of any visible residues on the equipment surface when inspected under defined lighting and distance conditions",
                 "Cleaned with a visual aid", "Clean enough for visual inspection only"],
     "answer": "The absence of any visible residues on the equipment surface when inspected under defined lighting and distance conditions",
     "explanation": "While 'visually clean' is a common acceptance criterion, it's often supplemented by analytical testing for specific residues to ensure thorough cleaning.",
     "source": "Cleaning Validation Principles, PIC/S PI 006"},
    {"difficulty": "hard", "question": "What is a 'Critical Defect' in product inspection?",
     "options": ["A defect that is hard to find",
                 "A defect that judgment and experience indicate is likely to result in hazardous or unsafe conditions for individuals using, maintaining, or depending upon the product; or a defect that judgment and experience indicate is likely to prevent performance of the tactical function of a major end item",
                 "Any visual defect", "A defect found by a critical inspector"],
     "answer": "A defect that judgment and experience indicate is likely to result in hazardous or unsafe conditions for individuals using, maintaining, or depending upon the product; or a defect that judgment and experience indicate is likely to prevent performance of the tactical function of a major end item",
     "explanation": "Critical defects typically lead to rejection of the batch or 100% inspection and rework if possible.",
     "source": "Sampling Plans (e.g., ANSI/ASQ Z1.4), Quality Control Principles"},
    {"difficulty": "hard", "question": "What is 'Acceptable Quality Limit' (AQL) in sampling plans?",
     "options": ["The best quality achievable",
                 "The maximum percent defective (or maximum number of defects per hundred units) that, for purposes of sampling inspection, can be considered satisfactory as a process average",
                 "A limit set by the QA manager", "A quality limit that is always zero defects"],
     "answer": "The maximum percent defective (or maximum number of defects per hundred units) that, for purposes of sampling inspection, can be considered satisfactory as a process average",
     "explanation": "AQL is a parameter of the sampling plan, not a guarantee that all batches meeting the AQL are defect-free. There's still a statistical risk of accepting lots with more defects.",
     "source": "ANSI/ASQ Z1.4, ISO 2859"},
    {"difficulty": "hard",
     "question": "What is the primary difference between 'Sterility Assurance Level' (SAL) and 'Sterility Testing'?",
     "options": ["SAL is for non-sterile products, sterility testing for sterile products",
                 "SAL is a calculated probability of a non-sterile unit (e.g., 10⁻⁶); sterility testing is a direct test on a sample of units to detect viable microorganisms",
                 "Sterility testing is more accurate than SAL", "SAL is determined by QA, sterility testing by QC"],
     "answer": "SAL is a calculated probability of a non-sterile unit (e.g., 10⁻⁶); sterility testing is a direct test on a sample of units to detect viable microorganisms",
     "explanation": "SAL is achieved through a validated sterilization process. Sterility testing has limitations due to the small sample size relative to the batch size.",
     "source": "Sterilization Principles, USP <1211>, <71>"},
    {"difficulty": "hard",
     "question": "What is a 'Certificate of Suitability to the monographs of the European Pharmacopoeia' (CEP)?",
     "options": ["A certificate for suitable employees",
                 "A certificate issued by the EDQM that demonstrates a substance's quality is suitably controlled by the relevant European Pharmacopoeia monograph(s)",
                 "A certificate of analysis from Europe", "A marketing authorization for Europe"],
     "answer": "A certificate issued by the EDQM that demonstrates a substance's quality is suitably controlled by the relevant European Pharmacopoeia monograph(s)",
     "explanation": "A CEP simplifies the regulatory process for using substances (APIs, excipients) in medicinal products within Europe and other regions recognizing CEPs.",
     "source": "EDQM (European Directorate for the Quality of Medicines & HealthCare)"},
    {"difficulty": "hard", "question": "What is the 'Common Technical Document' (CTD) format?",
     "options": ["A common document used for technical training",
                 "A harmonized format for regulatory submissions (e.g., NDAs, MAAs) developed by ICH, consisting of five modules",
                 "A technical document shared among companies", "A template for SOPs"],
     "answer": "A harmonized format for regulatory submissions (e.g., NDAs, MAAs) developed by ICH, consisting of five modules",
     "explanation": "The CTD format (Modules 1-5) facilitates the preparation and review of marketing applications across ICH regions (US, EU, Japan, etc.).",
     "source": "ICH M4 Guideline"},
    {"difficulty": "hard", "question": "What is 'Module 3' of the CTD primarily concerned with?",
     "options": ["Nonclinical study reports", "Clinical study reports",
                 "Quality (Chemistry, Manufacturing, and Controls - CMC)",
                 "Administrative information and prescribing information"],
     "answer": "Quality (Chemistry, Manufacturing, and Controls - CMC)",
     "explanation": "Module 3 contains detailed information on the drug substance and drug product, including manufacturing processes, characterization, specifications, and stability data.",
     "source": "ICH M4Q Guideline"},
    {"difficulty": "hard", "question": "What is the purpose of 'Process Capability Index' (e.g., Cpk, Ppk)?",
     "options": ["To measure how capable employees are",
                 "A statistical measure of a process's ability to produce output within specification limits",
                 "An index of all company processes", "A measure of process speed"],
     "answer": "A statistical measure of a process's ability to produce output within specification limits",
     "explanation": "A Cpk or Ppk value greater than 1.33 is often considered capable, though targets vary. Cpk considers process centering while Ppk reflects overall process performance.",
     "source": "Statistical Process Control (SPC) Principles"},
    {"difficulty": "hard", "question": "What is 'Out of Trend' (OOT) analysis?", "options": ["Analyzing fashion trends",
                                                                                             "A statistical evaluation of data over time to identify results that deviate from an expected pattern or historical performance, even if they are within specification limits",
                                                                                             "Analyzing trends in customer complaints",
                                                                                             "A type of financial trend analysis"],
     "answer": "A statistical evaluation of data over time to identify results that deviate from an expected pattern or historical performance, even if they are within specification limits",
     "explanation": "OOT analysis can provide early warnings of potential process drifts or issues before OOS results occur.",
     "source": "Quality Systems, Data Analysis"},
    {"difficulty": "hard",
     "question": "What is the primary challenge in validating 'Legacy Systems' (older computerized systems)?",
     "options": ["They are too old to validate",
                 "Lack of original documentation, vendor support, or understanding of the system's original design and development",
                 "Employees don't like using them", "They work perfectly so they don't need validation"],
     "answer": "Lack of original documentation, vendor support, or understanding of the system's original design and development",
     "explanation": "Validating legacy systems often requires a risk-based approach focusing on current functionality and impact on product quality and data integrity.",
     "source": "GAMP Good Practice Guide: Validation of Legacy Systems"},
    {"difficulty": "hard", "question": "What is 'Data Governance' in the context of data integrity?",
     "options": ["Governing who can access data",
                 "The sum total of arrangements to ensure that data, irrespective of the format in which it is generated, is recorded, processed, retained and used to ensure a complete, consistent and accurate record throughout the data lifecycle",
                 "A government department for data", "A type of data encryption"],
     "answer": "The sum total of arrangements to ensure that data, irrespective of the format in which it is generated, is recorded, processed, retained and used to ensure a complete, consistent and accurate record throughout the data lifecycle",
     "explanation": "Good data governance includes policies, procedures, training, and technical controls to ensure data integrity.",
     "source": "MHRA GxP Data Integrity Guidance"},
    {"difficulty": "hard", "question": "What is an 'Audit Trail' for a GxP computerized system?",
     "options": ["A trail leading to the audit room",
                 "A secure, computer-generated, time-stamped electronic record that allows for reconstruction of the course of events relating to the creation, modification, or deletion of an electronic record",
                 "A list of all audits performed", "A manual log of system changes"],
     "answer": "A secure, computer-generated, time-stamped electronic record that allows for reconstruction of the course of events relating to the creation, modification, or deletion of an electronic record",
     "explanation": "Audit trails are critical for data integrity, providing traceability of actions and changes to electronic records.",
     "source": "FDA 21 CFR Part 11, EU GMP Annex 11"},
    {"difficulty": "hard", "question": "What is 'Periodic Review' of validated systems/processes?",
     "options": ["Reviewing them only if there's a problem",
                 "A documented re-evaluation at scheduled intervals to confirm that a system or process remains in a validated state and continues to operate as intended",
                 "A quick daily check", "A review by an external auditor"],
     "answer": "A documented re-evaluation at scheduled intervals to confirm that a system or process remains in a validated state and continues to operate as intended",
     "explanation": "Periodic review ensures ongoing compliance and identifies any need for revalidation or changes.",
     "source": "Validation Principles, GAMP 5"},
    {"difficulty": "hard", "question": "What is a 'Genotoxic Impurity'?", "options": ["An impurity that is not toxic",
                                                                                      "An impurity that has been demonstrated to be mutagenic or clastogenic and is therefore presumed to have the potential to damage DNA and cause cancer in humans",
                                                                                      "An impurity from a gene therapy product",
                                                                                      "A very common impurity"],
     "answer": "An impurity that has been demonstrated to be mutagenic or clastogenic and is therefore presumed to have the potential to damage DNA and cause cancer in humans",
     "explanation": "Control of genotoxic impurities to very low levels (e.g., Threshold of Toxicological Concern - TTC) is a major regulatory concern.",
     "source": "ICH M7 Guideline"},
    {"difficulty": "hard", "question": "What is the 'Threshold of Toxicological Concern' (TTC) approach?",
     "options": ["A threshold for all toxic substances",
                 "A principle that establishes a human exposure threshold value for chemicals below which there is a very low probability of an appreciable risk to human health, used for certain unstudied impurities",
                 "A concern about toxicology", "A list of all toxic thresholds"],
     "answer": "A principle that establishes a human exposure threshold value for chemicals below which there is a very low probability of an appreciable risk to human health, used for certain unstudied impurities",
     "explanation": "The TTC approach is particularly relevant for controlling genotoxic impurities when specific toxicological data is lacking.",
     "source": "ICH M7"},
    {"difficulty": "hard", "question": "What is a 'Quality Target Product Profile' (QTPP)?",
     "options": ["The target profile for a quality employee",
                 "A prospective summary of the quality characteristics of a drug product that ideally will be achieved to ensure the desired quality, taking into account safety and efficacy",
                 "A profile of all quality targets in the company", "A marketing document describing product quality"],
     "answer": "A prospective summary of the quality characteristics of a drug product that ideally will be achieved to ensure the desired quality, taking into account safety and efficacy",
     "explanation": "The QTPP forms the basis for product and process development under a Quality by Design (QbD) approach.",
     "source": "ICH Q8(R2)"},
    {"difficulty": "hard", "question": "What is 'Control Strategy' in the context of ICH Q8, Q10, and Q11?",
     "options": ["A strategy to control employees",
                 "A planned set of controls, derived from product and process understanding, that assures process performance and product quality. The controls can include parameters and attributes related to drug substance and drug product materials and components, facility and equipment operating conditions, in-process controls, finished product specifications, and the associated methods and frequency of monitoring and control.",
                 "A strategy for pest control", "A document control strategy"],
     "answer": "A planned set of controls, derived from product and process understanding, that assures process performance and product quality. The controls can include parameters and attributes related to drug substance and drug product materials and components, facility and equipment operating conditions, in-process controls, finished product specifications, and the associated methods and frequency of monitoring and control.",
     "explanation": "A robust control strategy is a key output of QbD and ensures consistent product quality.",
     "source": "ICH Q8, Q10, Q11"},
    {"difficulty": "hard",
     "question": "What is 'Active Pharmaceutical Ingredient Starting Material' as defined by ICH Q7?",
     "options": ["Any material used to start API manufacturing",
                 "A raw material, intermediate, or an API that is used in the production of an API and that is incorporated as a significant structural fragment into the structure of the API. It is the point at which GMP requirements for API manufacturing begin.",
                 "The very first chemical purchased for a process", "A material that starts the chemical reaction"],
     "answer": "A raw material, intermediate, or an API that is used in the production of an API and that is incorporated as a significant structural fragment into the structure of the API. It is the point at which GMP requirements for API manufacturing begin.",
     "explanation": "The proper definition and justification of the API starting material is a critical regulatory expectation.",
     "source": "ICH Q7, ICH Q11"},
    {"difficulty": "hard", "question": "What is a 'Drug Master File' (DMF) or 'Active Substance Master File' (ASMF)?",
     "options": ["A master file for all drugs in a company",
                 "A submission to a regulatory authority containing confidential detailed information about facilities, processes, or articles used in the manufacturing, processing, packaging, and storing of one or more human drugs, often submitted by an API manufacturer to support an NDA/MAA from a drug product manufacturer",
                 "A file containing all master batch records", "A marketing file for a drug"],
     "answer": "A submission to a regulatory authority containing confidential detailed information about facilities, processes, or articles used in the manufacturing, processing, packaging, and storing of one or more human drugs, often submitted by an API manufacturer to support an NDA/MAA from a drug product manufacturer",
     "explanation": "DMFs/ASMFs allow API manufacturers to protect their intellectual property while providing necessary information to regulatory agencies and their customers.",
     "source": "FDA DMF Guidance, EMA ASMF Procedure"},
    {"difficulty": "hard",
     "question": "What is 'Process Analytical Technology (PAT) - Real Time Release Testing (RTRT)' according to ICH Q8?",
     "options": ["Testing products in real time for marketing",
                 "The ability to evaluate and ensure the quality of in-process and/or final product based on process data, which typically include a valid combination of measured material attributes and process controls, potentially replacing end-product testing",
                 "A very fast release test", "A technology for releasing PAT records"],
     "answer": "The ability to evaluate and ensure the quality of in-process and/or final product based on process data, which typically include a valid combination of measured material attributes and process controls, potentially replacing end-product testing",
     "explanation": "RTRT is an advanced application of PAT that can significantly improve manufacturing efficiency and quality assurance.",
     "source": "ICH Q8(R2)"},
    {"difficulty": "hard", "question": "What is the 'F0 value' in steam sterilization validation?",
     "options": ["The initial temperature",
                 "A measure of the lethality of a heat sterilization process, equivalent to the time in minutes at a reference temperature of 121.1°C (250°F) delivered to a product, assuming a Z-value of 10°C",
                 "The final outcome of sterilization", "A failure code for sterilization"],
     "answer": "A measure of the lethality of a heat sterilization process, equivalent to the time in minutes at a reference temperature of 121.1°C (250°F) delivered to a product, assuming a Z-value of 10°C",
     "explanation": "F0 is used to quantify the microbial inactivation achieved by a steam sterilization cycle.",
     "source": "Sterilization Principles, USP <1229.1>"},
    {"difficulty": "hard",
     "question": "What is a 'Bio-Decontamination Cycle' for an isolator or cleanroom (e.g., using VHP)?",
     "options": ["A routine cleaning cycle",
                 "A validated process using a sporicidal chemical agent (like Vaporized Hydrogen Peroxide - VHP) to achieve a defined level of microbial inactivation on exposed surfaces",
                 "Decontaminating biological samples", "A cycle to remove all biological life from the planet"],
     "answer": "A validated process using a sporicidal chemical agent (like Vaporized Hydrogen Peroxide - VHP) to achieve a defined level of microbial inactivation on exposed surfaces",
     "explanation": "This is crucial for preparing isolators and cleanrooms for aseptic operations, often targeting a 6-log reduction of resistant spores.",
     "source": "GMP Annex 1, Isolator Technology"},
    {"difficulty": "hard", "question": "What is the primary purpose of 'Bulk Product Holding Time' studies?",
     "options": ["To see how long bulk product can be stored before selling",
                 "To establish the maximum time that a bulk drug product can be held under specified conditions before further processing (e.g., filling) without adversely affecting its quality attributes",
                 "To validate the holding tanks", "To reduce storage costs"],
     "answer": "To establish the maximum time that a bulk drug product can be held under specified conditions before further processing (e.g., filling) without adversely affecting its quality attributes",
     "explanation": "These studies ensure that any delays in the manufacturing process do not compromise the final product quality.",
     "source": "Process Validation, Stability Principles"},
    {"difficulty": "hard", "question": "What is 'Atypical Result' or 'Aberrant Result' in laboratory testing?",
     "options": ["A result that is very good",
                 "A result that is unexpected, unusual, or inconsistent with historical data or other results, even if it is within specification limits",
                 "A result from an uncalibrated instrument", "A result that is always OOS"],
     "answer": "A result that is unexpected, unusual, or inconsistent with historical data or other results, even if it is within specification limits",
     "explanation": "Atypical results should trigger an investigation to understand their cause and potential impact, similar to OOS investigations but for in-specification results.",
     "source": "Laboratory Controls, OOS/OOT Guidance"},
    {"difficulty": "hard",
     "question": "What is the significance of the 'Recovery Factor' in cleaning validation swab/rinse sampling?",
     "options": ["How quickly the equipment recovers from cleaning",
                 "The percentage of a known amount of residue that can be recovered from a surface by a specific sampling method (swab or rinse) and quantified by the analytical method",
                 "The factor by which cleaning time is reduced", "How much cleaning agent is recovered"],
     "answer": "The percentage of a known amount of residue that can be recovered from a surface by a specific sampling method (swab or rinse) and quantified by the analytical method",
     "explanation": "The recovery factor must be determined and applied to calculate the actual amount of residue present on the equipment surface.",
     "source": "Cleaning Validation Principles, PIC/S PI 006"},
    {"difficulty": "hard", "question": "What is 'Worst Case Product' approach in cleaning validation?",
     "options": ["The product that is hardest to sell",
                 "Selecting the product that is most difficult to clean (e.g., due to low solubility, high toxicity, high concentration) to represent a group of similar products for cleaning validation purposes",
                 "The product with the most customer complaints", "The product made in the worst equipment"],
     "answer": "Selecting the product that is most difficult to clean (e.g., due to low solubility, high toxicity, high concentration) to represent a group of similar products for cleaning validation purposes",
     "explanation": "Validating the cleaning procedure for the worst-case product provides assurance for other products in the group, reducing overall validation effort.",
     "source": "Cleaning Validation Principles"},
    {"difficulty": "hard", "question": "What is a 'Pharmacokinetic (PK) Study' primarily designed to determine?",
     "options": ["How the drug affects the body (pharmacodynamics)",
                 "How the body affects the drug (absorption, distribution, metabolism, and excretion - ADME)",
                 "The drug's manufacturing process", "The drug's price"],
     "answer": "How the body affects the drug (absorption, distribution, metabolism, and excretion - ADME)",
     "explanation": "PK studies are essential for understanding a drug's dosing regimen, potential drug interactions, and behavior in different patient populations.",
     "source": "Pharmacology, Clinical Pharmacology"},
    {"difficulty": "hard", "question": "What is a 'Pharmacodynamic (PD) Study' primarily designed to determine?",
     "options": ["How the body affects the drug (ADME)",
                 "How the drug affects the body (the biochemical and physiological effects of drugs and their mechanisms of action)",
                 "The drug's stability", "The drug's packaging requirements"],
     "answer": "How the drug affects the body (the biochemical and physiological effects of drugs and their mechanisms of action)",
     "explanation": "PD studies help understand a drug's efficacy, mechanism, and dose-response relationship.",
     "source": "Pharmacology, Clinical Pharmacology"},
    {"difficulty": "hard", "question": "What is 'Statistical Significance' (e.g., p-value < 0.05) in data analysis?",
     "options": ["The data is very important",
                 "A measure of the probability that an observed difference or relationship could have occurred by random chance alone; a small p-value suggests the observed effect is likely real",
                 "The data is 100% correct", "The data is easy to understand"],
     "answer": "A measure of the probability that an observed difference or relationship could have occurred by random chance alone; a small p-value suggests the observed effect is likely real",
     "explanation": "Statistical significance does not necessarily imply practical or clinical significance, and the chosen alpha level (e.g., 0.05) is a convention.",
     "source": "Statistics Principles"},
    {"difficulty": "hard", "question": "What is a 'Confidence Interval' in statistics?",
     "options": ["How confident you are in the results",
                 "A range of values, derived from sample data, that is likely to contain the true value of an unknown population parameter with a certain degree of confidence (e.g., 95% CI)",
                 "An interval where data is always correct", "A type of data storage interval"],
     "answer": "A range of values, derived from sample data, that is likely to contain the true value of an unknown population parameter with a certain degree of confidence (e.g., 95% CI)",
     "explanation": "A narrower confidence interval indicates more precision in the estimate.",
     "source": "Statistics Principles"},
    {"difficulty": "hard", "question": "What is 'Process Drift'?", "options": ["When a process stops working",
                                                                               "A gradual change or shift in process performance or output over time, which may still be within specification limits but could indicate an underlying issue or a trend towards an out-of-control state",
                                                                               "A very fast process",
                                                                               "A planned change in a process"],
     "answer": "A gradual change or shift in process performance or output over time, which may still be within specification limits but could indicate an underlying issue or a trend towards an out-of-control state",
     "explanation": "Monitoring for process drift using control charts and trend analysis is important for maintaining a state of control.",
     "source": "Statistical Process Control (SPC)"},
    {"difficulty": "hard", "question": "What is 'Equipment History File/Log'?",
     "options": ["A file about the history of equipment in general",
                 "A record maintained for each significant piece of equipment, detailing its installation, calibration, maintenance, repairs, modifications, and usage history",
                 "A list of all equipment in the company", "A user manual for old equipment"],
     "answer": "A record maintained for each significant piece of equipment, detailing its installation, calibration, maintenance, repairs, modifications, and usage history",
     "explanation": "This file provides a complete lifecycle history for the equipment and is important for investigations, maintenance planning, and GMP compliance.",
     "source": "GMP Equipment Management"},
    {"difficulty": "hard", "question": "What is the role of 'Internal Audits' (Self-Inspections) in a PQS?",
     "options": ["To prepare for external audits only",
                 "A systematic and independent examination of a company's own quality systems and procedures to determine compliance with GMP and internal requirements, and to identify areas for improvement",
                 "A way to find fault with employees", "Performed only by external auditors"],
     "answer": "A systematic and independent examination of a company's own quality systems and procedures to determine compliance with GMP and internal requirements, and to identify areas for improvement",
     "explanation": "Internal audits are a proactive tool for maintaining compliance and driving continuous improvement.",
     "source": "ICH Q10, GMP Chapter 9 (Self Inspection)"},
    {"difficulty": "hard", "question": "What is 'Management of Outsourced Activities' as per ICH Q10?",
     "options": ["Hiring external managers",
                 "The PQS should extend to the control and review of any outsourced activities and the quality of purchased materials, ensuring that responsibilities are clearly defined in quality agreements",
                 "Outsourcing all management tasks", "Only for activities outsourced to other countries"],
     "answer": "The PQS should extend to the control and review of any outsourced activities and the quality of purchased materials, ensuring that responsibilities are clearly defined in quality agreements",
     "explanation": "The contract giver is ultimately responsible for the quality of outsourced activities and materials.",
     "source": "ICH Q10"},
    {"difficulty": "hard", "question": "What is a 'Product Lifecycle' approach in pharmaceutical quality systems?",
     "options": ["The time from when a product is launched until it is discontinued",
                 "A holistic view of a product from initial development, through manufacturing, distribution, and discontinuation, with quality management applied at all stages",
                 "The shelf life of a product", "The lifecycle of the product packaging"],
     "answer": "A holistic view of a product from initial development, through manufacturing, distribution, and discontinuation, with quality management applied at all stages",
     "explanation": "ICH Q8, Q9, and Q10 promote a lifecycle approach to ensure product quality is built-in and maintained.",
     "source": "ICH Q8, Q9, Q10"},
    {"difficulty": "hard", "question": "What is 'Dead Leg' in a pharmaceutical water system or piping?",
     "options": ["A pipe that is no longer used",
                 "A section of pipework where water can stagnate due to lack of flow, creating a potential for microbial growth and contamination",
                 "A support for a pipe", "A very short pipe"],
     "answer": "A section of pipework where water can stagnate due to lack of flow, creating a potential for microbial growth and contamination",
     "explanation": "Design of water systems aims to minimize or eliminate dead legs to maintain water quality.",
     "source": "Pharmaceutical Water System Design, ISPE Baseline Guide"},
    {"difficulty": "hard", "question": "What is 'Rouging' in stainless steel pharmaceutical systems?",
     "options": ["Painting stainless steel red",
                 "A form of corrosion (iron oxide deposition) that can occur on the surface of stainless steel in high-purity water or steam systems, appearing as a reddish or brownish film",
                 "A type of polishing for stainless steel", "A protective layer on stainless steel"],
     "answer": "A form of corrosion (iron oxide deposition) that can occur on the surface of stainless steel in high-purity water or steam systems, appearing as a reddish or brownish film",
     "explanation": "While often not a direct contamination risk itself, rouging can indicate underlying corrosion issues or trap contaminants, and needs to be monitored and managed.",
     "source": "Pharmaceutical Engineering, Water System Maintenance"},
    {"difficulty": "hard", "question": "What is 'Passivation' of stainless steel?",
     "options": ["Making stainless steel passive or inactive",
                 "A chemical treatment process that removes free iron from the surface of stainless steel and enhances the formation of a passive chromium oxide layer, improving its corrosion resistance",
                 "Painting stainless steel", "A type of cleaning for stainless steel"],
     "answer": "A chemical treatment process that removes free iron from the surface of stainless steel and enhances the formation of a passive chromium oxide layer, improving its corrosion resistance",
     "explanation": "Passivation is important for maintaining the integrity and cleanliness of stainless steel equipment and piping in pharmaceutical applications.",
     "source": "ASTM A967, Pharmaceutical Engineering"},
    {"difficulty": "hard",
     "question": "What is 'Total Organic Carbon' (TOC) testing used for in pharmaceutical water systems?",
     "options": ["To measure all carbon-based life forms",
                 "An indirect measure of organic molecules present in water, used as an indicator of water purity and to monitor the effectiveness of purification processes",
                 "To measure inorganic carbon", "A test for carbonated water"],
     "answer": "An indirect measure of organic molecules present in water, used as an indicator of water purity and to monitor the effectiveness of purification processes",
     "explanation": "Low TOC levels are required for Purified Water and Water for Injection.",
     "source": "USP <643>, EP 2.2.44"},
    {"difficulty": "hard", "question": "What is 'Conductivity' testing used for in pharmaceutical water systems?",
     "options": ["To test electrical conductivity of equipment",
                 "An indirect measure of the concentration of ionic impurities in water, used as an indicator of water purity",
                 "To measure water temperature", "A test for static electricity"],
     "answer": "An indirect measure of the concentration of ionic impurities in water, used as an indicator of water purity",
     "explanation": "High conductivity indicates higher levels of dissolved ions. It's a key quality attribute for pharmaceutical water.",
     "source": "USP <645>, EP 2.2.38"},
    {"difficulty": "hard", "question": "What is 'Aseptic Connection' in sterile manufacturing?",
     "options": ["Connecting two sterile items in any way",
                 "A procedure for connecting two or more sterile components (e.g., tubing, bags, filters) in a manner that maintains the sterility of the fluid pathway",
                 "A very clean connection", "A connection made by an aseptic operator"],
     "answer": "A procedure for connecting two or more sterile components (e.g., tubing, bags, filters) in a manner that maintains the sterility of the fluid pathway",
     "explanation": "This often involves specialized connectors (e.g., sterile connectors, steam-in-place connections) or techniques performed in a Grade A environment.",
     "source": "GMP Annex 1, Aseptic Processing Principles"},
    {"difficulty": "hard", "question": "What is 'Single-Use Technology (SUT) Validation' primarily focused on?",
     "options": ["Validating that it can be used only once",
                 "Ensuring the SUT components are sterile (if applicable), do not leach harmful substances into the product, maintain integrity under process conditions, and are suitable for their intended use",
                 "Validating the disposal process", "Testing the plastic material only"],
     "answer": "Ensuring the SUT components are sterile (if applicable), do not leach harmful substances into the product, maintain integrity under process conditions, and are suitable for their intended use",
     "explanation": "Key aspects include extractables/leachables, integrity testing, particulate control, and supplier qualification.",
     "source": "Bio-Process Systems Alliance (BPSA) Guides, PDA TR No. 66"},
    {"difficulty": "hard", "question": "What is a 'Holistic Validation Approach'?",
     "options": ["Validating the whole company at once",
                 "An approach that considers the entire system or process, including interactions between components, rather than validating individual parts in isolation, often emphasizing risk-based strategies and lifecycle management",
                 "A very spiritual validation method", "Validating only on holidays"],
     "answer": "An approach that considers the entire system or process, including interactions between components, rather than validating individual parts in isolation, often emphasizing risk-based strategies and lifecycle management",
     "explanation": "This integrated approach is more aligned with modern quality system thinking (e.g., ICH Q8, Q9, Q10).",
     "source": "Modern Validation Principles"},
    {"difficulty": "hard",
     "question": "What is 'Breakthrough Volume' in chromatography column packing or adsorption processes?",
     "options": ["The volume at which the column breaks",
                 "The volume of mobile phase (or sample) that can pass through a column before the analyte of interest or an impurity begins to elute or is no longer effectively retained",
                 "The volume of the first breakthrough discovery", "The total volume of the column"],
     "answer": "The volume of mobile phase (or sample) that can pass through a column before the analyte of interest or an impurity begins to elute or is no longer effectively retained",
     "explanation": "Knowing the breakthrough volume is important for optimizing purification processes and preventing product loss or contamination.",
     "source": "Chromatography Principles, Process Development"},
    {"difficulty": "hard", "question": "What is 'Process Signature' or 'Process Fingerprint' in PAT?",
     "options": ["The signature of the process owner",
                 "A unique multivariate data profile or pattern generated by a process when it is operating in a state of control, which can be used for real-time monitoring and fault detection",
                 "A fingerprint left on the equipment", "A simplified process diagram"],
     "answer": "A unique multivariate data profile or pattern generated by a process when it is operating in a state of control, which can be used for real-time monitoring and fault detection",
     "explanation": "Deviations from the established process signature can indicate potential issues.",
     "source": "Process Analytical Technology (PAT) Principles"},
    {"difficulty": "hard", "question": "What is 'Chemometrics'?", "options": ["Measuring chemicals",
                                                                              "The science of extracting information from chemical systems by data-driven means, often using multivariate statistical methods to analyze complex chemical data (e.g., from spectroscopic instruments in PAT)",
                                                                              "A type of chemical metric system",
                                                                              "The chemistry of metrics"],
     "answer": "The science of extracting information from chemical systems by data-driven means, often using multivariate statistical methods to analyze complex chemical data (e.g., from spectroscopic instruments in PAT)",
     "explanation": "Chemometrics is essential for developing predictive models and control strategies in PAT applications.",
     "source": "Analytical Chemistry, PAT"},
    {"difficulty": "hard",
     "question": "What is a 'Regulatory Starting Material' (RSM) in API synthesis, and why is its definition critical?",
     "options": ["The first material purchased for API synthesis; it's not very critical",
                 "A material used in the synthesis of an API that is incorporated as a significant structural fragment into the API structure. Its definition is critical because GMP controls typically apply from this point forward in the synthesis.",
                 "Any starting material regulated by the government", "A material that starts the regulatory process"],
     "answer": "A material used in the synthesis of an API that is incorporated as a significant structural fragment into the API structure. Its definition is critical because GMP controls typically apply from this point forward in the synthesis.",
     "explanation": "The selection and justification of RSMs are scrutinized by regulatory agencies as it defines the scope of GMP for API manufacturing.",
     "source": "ICH Q11 Development and Manufacture of Drug Substances"},
    {"difficulty": "hard",
     "question": "What is the 'Maximum Allowable Carryover' (MACRO) or 'Acceptable Daily Exposure' (ADE) used for in cleaning validation limit calculations?",
     "options": ["The maximum amount of product that can be carried over to the next office",
                 "A health-based limit representing the maximum amount of a residue of one product that can be carried over into a subsequent product without posing an unacceptable risk to patient safety",
                 "The amount of cleaning agent allowed", "A limit for how much can be carried by one person"],
     "answer": "A health-based limit representing the maximum amount of a residue of one product that can be carried over into a subsequent product without posing an unacceptable risk to patient safety",
     "explanation": "ADE (derived from toxicological data) is increasingly the preferred method for setting scientifically sound cleaning limits, replacing older 10 ppm or 1/1000th dose criteria where appropriate.",
     "source": "EMA Guideline on setting health based exposure limits, ISPE Risk-MaPP Guide"},
    {"difficulty": "hard", "question": "What is 'Orthogonal Analytical Methods'?",
     "options": ["Methods that are perpendicular to each other",
                 "The use of two or more analytical methods based on different scientific principles to measure the same attribute or analyte, providing greater confidence in the results",
                 "Methods developed by Dr. Orthogonal", "Very complex analytical methods"],
     "answer": "The use of two or more analytical methods based on different scientific principles to measure the same attribute or analyte, providing greater confidence in the results",
     "explanation": "If different methods yield comparable results, it strengthens the validity of the data, especially for critical quality attributes or impurity profiling.",
     "source": "Analytical Method Development & Validation"},
    {"difficulty": "hard",
     "question": "What does 'Lifecycle Management of Analytical Procedures' (as per upcoming USP <1220> / ICH Q14) emphasize?",
     "options": ["Using analytical procedures only once in their lifecycle",
                 "A holistic approach to analytical procedures, from development and validation through routine use and retirement, focusing on ensuring continued fitness for purpose based on risk and knowledge management",
                 "The lifecycle of the analyst performing the procedure",
                 "Only validating the procedure once at the beginning"],
     "answer": "A holistic approach to analytical procedures, from development and validation through routine use and retirement, focusing on ensuring continued fitness for purpose based on risk and knowledge management",
     "explanation": "This modern approach moves away from a one-time validation event towards continuous verification and improvement of analytical procedures.",
     "source": "USP <1220> Analytical Procedure Lifecycle, ICH Q14 Analytical Procedure Development"},
    {"difficulty": "hard", "question": "What is 'Material Qualification' in the context of single-use systems (SUS)?",
     "options": ["Qualifying the person who uses the material",
                 "Evaluating the suitability of the materials of construction of SUS components, including biocompatibility, extractables/leachables profiles, and physical/chemical properties, for the intended application",
                 "Testing if the material is qualified to be single-use", "Only checking the supplier's certificate"],
     "answer": "Evaluating the suitability of the materials of construction of SUS components, including biocompatibility, extractables/leachables profiles, and physical/chemical properties, for the intended application",
     "explanation": "This is critical to ensure the SUS does not adversely affect product quality or patient safety.",
     "source": "BPSA Guides, PDA TR No. 66"},
    {"difficulty": "hard", "question": "What is 'Viral Clearance Validation' for biopharmaceutical products?",
     "options": ["Validating that the product is clear of viruses by visual inspection",
                 "Documented evidence that the manufacturing process (specifically certain purification steps) can effectively remove or inactivate a range of viruses that could potentially contaminate the product",
                 "Validating the antiviral properties of the drug", "Cleaning viruses from the facility"],
     "answer": "Documented evidence that the manufacturing process (specifically certain purification steps) can effectively remove or inactivate a range of viruses that could potentially contaminate the product",
     "explanation": "This is a critical safety requirement for products derived from cell lines or biological sources, often involving spiking studies with model viruses.",
     "source": "ICH Q5A (R1)"},
]

# --- Bot Configuration & Handlers ---
QUIZ_LENGTH = 20
QUIZ_COMPOSITION = {"easy": 7, "medium": 7, "hard": 6}
ENCOURAGING_PHRASES = [
    "Every quiz is a step forward in mastering GMP! �",
    "Keep up the great work! Repetition is key to learning. 🧠",
    "Don't be discouraged by mistakes, they are learning opportunities. 🌱",
    "Your GMP knowledge is growing with each attempt! 💪",
    "Challenge yourself again and see how much you've improved! 📈",
    "GMP expertise is built one question at a time. You're doing great! ✨"
]

# States for conversation
WELCOME, IN_QUIZ, RESULTS_DISPLAYED, REVIEW_QUESTIONS = range(4)


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "🚀 Begin/Restart GMP Assessment"),
        BotCommand("cancel", "❌ Cancel current action"),
    ])
    logger.info("Bot commands set successfully.")


def store_quiz_entry(context: ContextTypes.DEFAULT_TYPE, question_data, user_answer_text, is_correct):
    """Stores the details of the answered question for later review."""
    if 'quiz_history' not in context.user_data:
        context.user_data['quiz_history'] = []

    context.user_data['quiz_history'].append({
        'question_text': question_data['question'],
        'options': question_data['options'],
        'user_answer_text': user_answer_text,
        'correct_answer_text': question_data['answer'],
        'is_correct': is_correct,
        'explanation': question_data.get('explanation', 'No explanation available for this question.'),
        'difficulty': question_data['difficulty']
    })


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_index = context.user_data.get("question_index", 0)
    quiz_questions = context.user_data.get("quiz_questions", [])

    if not quiz_questions or question_index >= len(quiz_questions):
        logger.warning("ask_question: No questions or index out of bounds. Attempting to show results.")
        await show_results_message(update, context)
        return ConversationHandler.END

    question_data = quiz_questions[question_index]
    question_text = (
        f"🎓 *Question {question_index + 1}/{QUIZ_LENGTH}* "
        f"(Difficulty: {question_data['difficulty'].capitalize()})\n\n"
        f"{question_data['question']}"
    )
    options_text = question_data["options"]

    shuffled_options_with_original_indices = list(enumerate(options_text))
    random.shuffle(shuffled_options_with_original_indices)

    context.user_data["current_original_options"] = options_text
    context.user_data["current_shuffled_options_display_map"] = {
        str(original_idx): opt_text for original_idx, opt_text in shuffled_options_with_original_indices
    }

    keyboard = []
    for original_idx, option_text_val in shuffled_options_with_original_indices:
        display_option_text = (option_text_val[:60] + '...') if len(option_text_val) > 63 else option_text_val
        keyboard.append([InlineKeyboardButton(display_option_text, callback_data=str(original_idx))])

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        target_message = update.callback_query.message if update.callback_query else update.message
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=question_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )
        elif update.message:
            await update.message.reply_text(
                text=question_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
            )
    except Exception as e:
        logger.error(f"Error in ask_question (edit/reply): {e}. Chat ID: {update.effective_chat.id}")
        error_message_text = "Error displaying question. Please try /start again."
        # Fallback: send a new message if edit fails
        if update.effective_chat:  # Ensure we have a chat to reply to
            await context.bot.send_message(chat_id=update.effective_chat.id, text=error_message_text)


async def show_results_message(update: Update, context: ContextTypes.DEFAULT_TYPE, from_review=False):
    user_data = context.user_data
    score = user_data.get("score", 0)

    if QUIZ_LENGTH == 0:
        percentage = 0.0
    else:
        percentage = (score / QUIZ_LENGTH) * 100

    if percentage >= 90:
        level = "🌟 *Expert*"
        comment = "Outstanding knowledge of GMP principles! Excellent work."
    elif percentage >= 75:
        level = "✅ *Advanced*"
        comment = "Strong understanding of GMP requirements. Well done."
    elif percentage >= 50:
        level = "🟡 *Intermediate*"
        comment = "Good foundational knowledge with room to grow."
    elif percentage >= 30:
        level = "🔸 *Basic*"
        comment = "Some understanding, but further study is recommended."
    else:
        level = "🔴 *Beginner*"
        comment = "Consider foundational GMP training to improve your knowledge."

    encouragement = random.choice(ENCOURAGING_PHRASES)

    result_message = f"""
📊 *Assessment Complete* 📊

✅ *Correct Answers:* {score}/{QUIZ_LENGTH}
📈 *Percentage:* {percentage:.1f}%
🏆 *Proficiency Level:* {level}

💡 *Recommendation:* {comment}

"{encouragement}"

What would you like to do next?
"""
    keyboard = [
        [InlineKeyboardButton("🔍 Review Answers", callback_data="review_start")],
        [InlineKeyboardButton("🚀 New Quiz", callback_data="new_quiz_from_results")],
        [InlineKeyboardButton("🏁 End Session", callback_data="end_session")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    target_message = update.callback_query.message if update.callback_query else update.message
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text=result_message, reply_markup=reply_markup,
                                                          parse_mode=ParseMode.MARKDOWN)
        elif update.message:
            await update.message.reply_text(text=result_message, reply_markup=reply_markup,
                                            parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(
            f"Error in show_results_message editing/sending message: {e}. Chat ID: {target_message.chat_id if target_message else 'N/A'}")
        if target_message:  # Fallback if edit fails
            await context.bot.send_message(chat_id=target_message.chat_id, text=result_message,
                                           reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return RESULTS_DISPLAYED


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()

    welcome_message = """
🌟 *Welcome to the GMP Proficiency Assessment Bot!* 🌟

This tool will test your knowledge of Good Manufacturing Practices (GMP) with a random selection of 20 questions.

The quiz includes questions from three difficulty levels:
• *Easy:* 7 questions
• *Medium:* 7 questions
• *Hard:* 6 questions

Ready to challenge your GMP knowledge? Click 'Start Assessment' below!
You can type /cancel at any point to stop the current assessment.
"""
    keyboard = [[InlineKeyboardButton("Start Assessment ✅", callback_data="initiate_quiz_setup")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            welcome_message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    return WELCOME


async def initiate_quiz_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    target_message = query.message if query else update.message  # For sending error messages

    if query:
        await query.answer()

    try:
        easy_q = [q for q in ALL_QUESTIONS if q['difficulty'] == 'easy']
        medium_q = [q for q in ALL_QUESTIONS if q['difficulty'] == 'medium']
        hard_q = [q for q in ALL_QUESTIONS if q['difficulty'] == 'hard']

        if len(easy_q) < QUIZ_COMPOSITION['easy'] or \
                len(medium_q) < QUIZ_COMPOSITION['medium'] or \
                len(hard_q) < QUIZ_COMPOSITION['hard']:
            logger.error("Not enough questions in one or more difficulty categories.")
            error_text = "❌ *Error:* Insufficient questions. Please contact admin."
            if query:
                await query.edit_message_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
            elif target_message:
                await target_message.reply_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
            return ConversationHandler.END

        quiz_questions = (
                random.sample(easy_q, QUIZ_COMPOSITION['easy']) +
                random.sample(medium_q, QUIZ_COMPOSITION['medium']) +
                random.sample(hard_q, QUIZ_COMPOSITION['hard'])
        )
        random.shuffle(quiz_questions)

        context.user_data.clear()
        context.user_data["quiz_questions"] = quiz_questions
        context.user_data["question_index"] = 0
        context.user_data["score"] = 0
        context.user_data["quiz_history"] = []

        await ask_question(update, context)
        return IN_QUIZ

    except ValueError as e:
        logger.error(f"ValueError during question sampling: {e}")
        error_text = "❌ *Error:* Not enough unique questions. Contact admin."
        if query:
            await query.edit_message_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
        elif target_message:
            await target_message.reply_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Unexpected error in initiate_quiz_setup: {e}")
        error_text = "❌ *Unexpected error.* Try /start."
        if query:
            await query.edit_message_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
        elif target_message:
            await target_message.reply_text(text=error_text, parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    user_data = context.user_data
    question_index = user_data.get("question_index", 0)
    quiz_questions = user_data.get("quiz_questions", [])
    original_options = user_data.get("current_original_options", [])

    if not quiz_questions or question_index >= len(quiz_questions) or not original_options:
        logger.warning(f"handle_answer called with incomplete quiz data for user {update.effective_user.id}.")
        await query.edit_message_text(text="Error: Quiz data is incomplete. Please /start again.",
                                      parse_mode=ParseMode.MARKDOWN)
        user_data.clear()
        return ConversationHandler.END

    current_question_data = quiz_questions[question_index]
    correct_answer_text = current_question_data["answer"]

    try:
        user_answer_original_index = int(query.data)
        user_selected_option_text = original_options[user_answer_original_index]
    except (ValueError, IndexError, TypeError) as e:  # Added TypeError for safety
        logger.error(
            f"Error processing user answer index: {e}. query.data: {query.data}, original_options length: {len(original_options)}")
        await query.edit_message_text(text="Error processing your answer. Please try /start again.",
                                      parse_mode=ParseMode.MARKDOWN)
        user_data.clear()
        return ConversationHandler.END

    is_correct = user_selected_option_text == correct_answer_text
    if is_correct:
        user_data["score"] = user_data.get("score", 0) + 1
        feedback = "✅ Correct!"
    else:
        feedback = f"❌ Incorrect. The correct answer was: *{correct_answer_text}*"

    store_quiz_entry(context, current_question_data, user_selected_option_text, is_correct)

    question_text_header = (
        f"🎓 *Question {question_index + 1}/{QUIZ_LENGTH}* "
        f"(Difficulty: {current_question_data['difficulty'].capitalize()})\n\n"
        f"{current_question_data['question']}"
    )
    try:
        await query.edit_message_text(
            text=f"{question_text_header}\n\n{feedback}", parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error editing message for feedback: {e}")

    await asyncio.sleep(1.5)  # Reduced sleep time

    user_data["question_index"] = question_index + 1

    if user_data["question_index"] < QUIZ_LENGTH and user_data["question_index"] < len(quiz_questions):
        await ask_question(update, context)
        return IN_QUIZ
    else:
        return await show_results_message(update, context)


async def review_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    quiz_history = context.user_data.get('quiz_history', [])
    if not quiz_history:
        await query.edit_message_text("No quiz history found to review. Try a new quiz with /start!",
                                      parse_mode=ParseMode.MARKDOWN)
        return RESULTS_DISPLAYED  # Or ConversationHandler.END if preferred

    context.user_data['review_index'] = 0
    await display_review_question(update, context)
    return REVIEW_QUESTIONS


async def display_review_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    review_index = context.user_data.get('review_index', 0)
    quiz_history = context.user_data.get('quiz_history', [])
    query = update.callback_query  # Should always be a query here

    if not quiz_history or not (0 <= review_index < len(quiz_history)):
        logger.warning(f"display_review_question: Invalid review_index {review_index} or empty history.")
        await query.edit_message_text("Review ended or history is unavailable.", parse_mode=ParseMode.MARKDOWN)
        return await show_results_message(update, context, from_review=True)

    item = quiz_history[review_index]

    result_icon = "✅" if item['is_correct'] else "❌"
    review_text = (
        f"🔍 *Review: Question {review_index + 1}/{len(quiz_history)}*\n"
        f"*(Difficulty: {item['difficulty'].capitalize()})*\n\n"
        f"*{item['question_text']}*\n\n"
        f"Your Answer: {item['user_answer_text']} {result_icon}\n"
    )
    if not item['is_correct']:
        review_text += f"Correct Answer: *{item['correct_answer_text']}*\n"

    explanation = item.get('explanation', 'No explanation available.')
    if explanation:  # Ensure explanation is not None or empty before adding title
        review_text += f"\n*Explanation:*\n_{explanation}_"

    keyboard_buttons = []
    nav_row = []
    if review_index > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data="review_prev"))

    nav_row.append(InlineKeyboardButton("🏁 End Review", callback_data="review_end"))

    if review_index < len(quiz_history) - 1:
        nav_row.append(InlineKeyboardButton("➡️ Next", callback_data="review_next"))

    keyboard_buttons.append(nav_row)
    reply_markup = InlineKeyboardMarkup(keyboard_buttons)

    try:
        await query.edit_message_text(text=review_text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error displaying review question: {e}")
        await query.message.reply_text("Error displaying review. Try /start.", parse_mode=ParseMode.MARKDOWN)


async def navigate_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    action = query.data

    review_index = context.user_data.get('review_index', 0)
    quiz_history_length = len(context.user_data.get('quiz_history', []))

    if action == "review_next" and review_index < quiz_history_length - 1:
        context.user_data['review_index'] += 1
    elif action == "review_prev" and review_index > 0:
        context.user_data['review_index'] -= 1

    await display_review_question(update, context)
    return REVIEW_QUESTIONS


async def end_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    final_message = (
        "Review finished! We hope this was helpful. 👍\n\n"
        "Ready for another round or want to explore more? "
        "Type /start to begin a new GMP assessment anytime. Keep learning and growing! 🌟"
    )
    try:
        # Edit the current review message to the final message, without navigation buttons
        await query.edit_message_text(text=final_message, reply_markup=None, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error editing message on end_review: {e}")
        # Fallback: send a new message if edit fails
        await query.message.reply_text(text=final_message, parse_mode=ParseMode.MARKDOWN)

    # Clear only review-specific data, keep score and history for potential re-display
    context.user_data.pop('review_index', None)
    # Do not clear user_data entirely here, as they might want to go back to score screen
    # or start a new quiz which would then clear it.
    # Transition back to results display state to show score and options again.
    return await show_results_message(update, context, from_review=True)


async def end_session_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    end_message = "Thanks for taking the GMP assessment! Type /start to begin a new one anytime. Keep learning! ✨"
    try:
        await query.edit_message_text(text=end_message, reply_markup=None, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error editing message on end_session_callback: {e}")
        await query.message.reply_text(text=end_message, parse_mode=ParseMode.MARKDOWN)

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message_text = "❌ Assessment cancelled. Type /start to begin again."

    if update.message:
        await update.message.reply_text(message_text)
    elif update.callback_query:
        try:
            current_message_text = update.callback_query.message.text
            # Avoid editing if message is already the cancellation message or similar
            if "cancelled" not in current_message_text.lower() and "assessment complete" not in current_message_text.lower():
                await update.callback_query.edit_message_text(text="Assessment has been cancelled.", reply_markup=None,
                                                              parse_mode=ParseMode.MARKDOWN)
            else:  # If already cancelled or quiz ended, just send a new confirmation
                await update.callback_query.message.reply_text(message_text)

        except Exception as e:
            logger.info(f"Could not edit message on cancel callback: {e}")
            await update.callback_query.message.reply_text(message_text)
        await update.callback_query.answer()

    logger.info(f"User {update.effective_user.id} cancelled the action.")
    context.user_data.clear()
    return ConversationHandler.END


def main() -> None:
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found. Please check your .env file or environment variables.")
        return

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    quiz_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [
                CallbackQueryHandler(initiate_quiz_setup, pattern="^initiate_quiz_setup$")
            ],
            IN_QUIZ: [
                CallbackQueryHandler(handle_answer),
            ],
            RESULTS_DISPLAYED: [
                CallbackQueryHandler(review_start, pattern="^review_start$"),
                CallbackQueryHandler(initiate_quiz_setup, pattern="^new_quiz_from_results$"),  # Re-initiate quiz
                CallbackQueryHandler(end_session_callback, pattern="^end_session$")
            ],
            REVIEW_QUESTIONS: [
                CallbackQueryHandler(navigate_review, pattern="^review_next$|^review_prev$"),
                CallbackQueryHandler(end_review, pattern="^review_end$")
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
        per_chat=True,
    )

    application.add_handler(quiz_conv)

    logger.info("GMP Assessment Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()
