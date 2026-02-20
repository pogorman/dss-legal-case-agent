/**
 * DSS Legal Case Intelligence — Case Browser Panel
 * Read-only view of structured case data for demo audience.
 */

const CaseBrowser = (function () {
  "use strict";

  // Backend URL — uses the same /chat API base but hits the case endpoints via APIM
  // For the browser, we proxy through the Container App or directly hit APIM
  const API_BASE_URL = window.__API_BASE_URL || "";

  const caseListEl = document.getElementById("caseList");
  const caseDetailEl = document.getElementById("caseDetail");

  let casesData = [];

  // ---- Synthetic Data (embedded for offline/SWA use) ----
  // This data mirrors seed.sql so the Case Browser works without API calls.
  const EMBEDDED_CASES = [
    {
      case_id: "2023-DR-02-0423",
      case_title: "DSS v. Murphy — CPS",
      case_type: "Child Protective Services",
      circuit: "Fifth Judicial Circuit",
      county: "Richland",
      filed_date: "2023-10-29",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Protective Services case involving Jalen Murphy (age 11) and Nia Murphy (age 6). Children removed after parent failed to seek medical attention for child injuries. Shonda Murphy ordered to complete treatment plan including random drug screening, domestic violence intervention program, psychological evaluation. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Shonda Murphy", role: "Parent", relationship: "Mother of Jalen Murphy (age 11) and Nia Murphy (age 6)" },
        { full_name: "Tyrone Murphy", role: "Parent", relationship: "Father of Jalen Murphy (age 11) and Nia Murphy (age 6)" },
        { full_name: "Jalen Murphy", role: "Child", relationship: "Minor child, age 11" },
        { full_name: "Nia Murphy", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Sandra Reeves", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Valerie Dunn", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2023-DR-05-0409",
      case_title: "DSS v. Stewart — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Second Judicial Circuit",
      county: "Barnwell",
      filed_date: "2023-07-03",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Janiya Stewart (age 2). Children removed after children left unsupervised for extended period. Gerald Stewart ordered to complete treatment plan including family therapy sessions, substance abuse evaluation and treatment, parenting skills classes (12 weeks), anger management classes, stable housing. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Diane Nelson", role: "Parent", relationship: "Mother of Janiya Stewart (age 2)" },
        { full_name: "Gerald Stewart", role: "Parent", relationship: "Father of Janiya Stewart (age 2)" },
        { full_name: "Janiya Stewart", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "David Ortiz", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Karen Milford", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 6,
      discrepancy_count: 3,
    },
    {
      case_id: "2023-DR-19-0360",
      case_title: "DSS v. Rogers — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Tenth Judicial Circuit",
      county: "Anderson",
      filed_date: "2024-07-03",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Nia Rogers (age 14) and Jaylen Rogers (age 6). Andre Rogers completed court-ordered treatment plan including substance abuse evaluation and treatment and random drug screening. Children successfully reunified with Andre Rogers under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Latoya Perez", role: "Parent", relationship: "Mother of Nia Rogers (age 14) and Jaylen Rogers (age 6)" },
        { full_name: "Andre Rogers", role: "Parent", relationship: "Father of Nia Rogers (age 14) and Jaylen Rogers (age 6)" },
        { full_name: "Nia Rogers", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Jaylen Rogers", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Cheryl Washington", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 7,
      discrepancy_count: 4,
    },
    {
      case_id: "2023-DR-22-0289",
      case_title: "DSS v. Morgan — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Third Judicial Circuit",
      county: "Sumter",
      filed_date: "2023-04-29",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Nia Morgan (age 14). Children removed after parent found to be incapacitated due to substance use while children were present. Sharon Morgan ordered to complete treatment plan including family therapy sessions, gainful employment, parenting skills classes (12 weeks). Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Sharon Morgan", role: "Parent", relationship: "Mother of Nia Morgan (age 14)" },
        { full_name: "Jamal Morgan", role: "Parent", relationship: "Father of Nia Morgan (age 14)" },
        { full_name: "Nia Morgan", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Jennifer Tate", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Raymond Holt", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 8,
      discrepancy_count: 4,
    },
    {
      case_id: "2023-DR-24-0355",
      case_title: "DSS v. Baker — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Seventh Judicial Circuit",
      county: "Spartanburg",
      filed_date: "2025-06-03",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Malik Baker (age 2). Children removed after parent failed to seek medical attention for child injuries. Gloria Baker ordered to complete treatment plan including domestic violence intervention program, random drug screening, stable housing, individual counseling. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Gloria Baker", role: "Parent", relationship: "Mother of Malik Baker (age 2)" },
        { full_name: "Gerald Baker", role: "Parent", relationship: "Father of Malik Baker (age 2)" },
        { full_name: "Malik Baker", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "Brian Colbert", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 6,
      discrepancy_count: 3,
    },
    {
      case_id: "2023-DR-25-0194",
      case_title: "DSS v. Williams — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fifth Judicial Circuit",
      county: "Kershaw",
      filed_date: "2024-05-09",
      status: "Dismissed",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Chloe Williams (age 4) and Aaliyah Williams (age 12). Investigation found insufficient evidence to substantiate allegations. Case dismissed by Judge Margaret Easley.",
      people: [
        { full_name: "Rhonda Williams", role: "Parent", relationship: "Mother of Chloe Williams (age 4) and Aaliyah Williams (age 12)" },
        { full_name: "Terrence Williams", role: "Parent", relationship: "Father of Chloe Williams (age 4) and Aaliyah Williams (age 12)" },
        { full_name: "Chloe Williams", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Aaliyah Williams", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Cheryl Washington", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Valerie Dunn", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 6,
      discrepancy_count: 3,
    },
    {
      case_id: "2023-DR-32-0273",
      case_title: "DSS v. Robinson — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Fifteenth Judicial Circuit",
      county: "Horry",
      filed_date: "2025-03-08",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Amari Robinson (age 6) and Gabrielle Robinson (age 3). Children removed after parent failed to seek medical attention for child injuries. Vanessa Robinson ordered to complete treatment plan including stable housing, random drug screening, individual counseling. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Vanessa Robinson", role: "Parent", relationship: "Mother of Amari Robinson (age 6) and Gabrielle Robinson (age 3)" },
        { full_name: "Travis Robinson", role: "Parent", relationship: "Father of Amari Robinson (age 6) and Gabrielle Robinson (age 3)" },
        { full_name: "Amari Robinson", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Gabrielle Robinson", role: "Child", relationship: "Minor child, age 3" },
        { full_name: "Andrea Foster", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Debra Whitfield", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 7,
      discrepancy_count: 2,
    },
    {
      case_id: "2023-DR-34-0302",
      case_title: "DSS v. Young — Physical Abuse",
      case_type: "Physical Abuse",
      circuit: "Fourth Judicial Circuit",
      county: "Darlington",
      filed_date: "2025-03-21",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Physical Abuse case involving Keyana Young (age 14) and Ebony Young (age 4). Children removed after home environment found to be unsanitary with animal waste and spoiled food. Christopher Young ordered to complete treatment plan including substance abuse evaluation and treatment, family therapy sessions, domestic violence intervention program. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Charlene Young", role: "Parent", relationship: "Mother of Keyana Young (age 14) and Ebony Young (age 4)" },
        { full_name: "Christopher Young", role: "Parent", relationship: "Father of Keyana Young (age 14) and Ebony Young (age 4)" },
        { full_name: "Keyana Young", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Ebony Young", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Tamara Hughes", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 6,
      discrepancy_count: 4,
    },
    {
      case_id: "2023-DR-43-0302",
      case_title: "DSS v. Holloway — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Eleventh Judicial Circuit",
      county: "McCormick",
      filed_date: "2024-05-09",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Xavier Holloway (age 1) and Aaliyah Holloway (age 12). Children removed after parent arrested on drug charges with children in vehicle. Nicole Holloway ordered to complete treatment plan including random drug screening, anger management classes, domestic violence intervention program, psychological evaluation, individual counseling. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Nicole Holloway", role: "Parent", relationship: "Mother of Xavier Holloway (age 1) and Aaliyah Holloway (age 12)" },
        { full_name: "Christopher Holloway", role: "Parent", relationship: "Father of Xavier Holloway (age 1) and Aaliyah Holloway (age 12)" },
        { full_name: "Xavier Holloway", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Aaliyah Holloway", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Sandra Reeves", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 5,
      discrepancy_count: 4,
    },
    {
      case_id: "2023-DR-43-0424",
      case_title: "DSS v. Wilson — Physical Abuse",
      case_type: "Physical Abuse",
      circuit: "Fourteenth Judicial Circuit",
      county: "Jasper",
      filed_date: "2023-06-04",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Physical Abuse case involving Bryce Wilson (age 9). Children removed after home environment found to be unsanitary with animal waste and spoiled food. Clifton Wilson ordered to complete treatment plan including stable housing, random drug screening, anger management classes, psychological evaluation, domestic violence intervention program. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Brenda Wilson", role: "Parent", relationship: "Mother of Bryce Wilson (age 9)" },
        { full_name: "Clifton Wilson", role: "Parent", relationship: "Father of Bryce Wilson (age 9)" },
        { full_name: "Bryce Wilson", role: "Child", relationship: "Minor child, age 9" },
        { full_name: "Renee Dawson", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-01-0537",
      case_title: "DSS v. Morris — Guardianship",
      case_type: "Guardianship",
      circuit: "Sixteenth Judicial Circuit",
      county: "Union",
      filed_date: "2023-05-25",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Guardianship case involving Serenity Morris (age 6). Children removed after children left unsupervised for extended period. Vernon Morris ordered to complete treatment plan including gainful employment, domestic violence intervention program, substance abuse evaluation and treatment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Iris Cook", role: "Parent", relationship: "Mother of Serenity Morris (age 6)" },
        { full_name: "Vernon Morris", role: "Parent", relationship: "Father of Serenity Morris (age 6)" },
        { full_name: "Serenity Morris", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "James Patterson", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 7,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-08-0394",
      case_title: "DSS v. Webb — CPS",
      case_type: "Child Protective Services",
      circuit: "Thirteenth Judicial Circuit",
      county: "Greenville",
      filed_date: "2025-05-01",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Protective Services case involving Bryce Webb (age 11). Children removed after parent arrested on drug charges with children in vehicle. Sabrina Webb ordered to complete treatment plan including substance abuse evaluation and treatment, stable housing, parenting skills classes (12 weeks). Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Sabrina Webb", role: "Parent", relationship: "Mother of Bryce Webb (age 11)" },
        { full_name: "Corey Webb", role: "Parent", relationship: "Father of Bryce Webb (age 11)" },
        { full_name: "Bryce Webb", role: "Child", relationship: "Minor child, age 11" },
        { full_name: "Lisa Fontaine", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 7,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-09-0365",
      case_title: "DSS v. Harris — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Ninth Judicial Circuit",
      county: "Charleston",
      filed_date: "2023-10-13",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Micah Harris (age 8). Vanessa Nelson completed court-ordered treatment plan including domestic violence intervention program and individual counseling. Children successfully reunified with Vanessa Nelson under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Vanessa Nelson", role: "Parent", relationship: "Mother of Micah Harris (age 8)" },
        { full_name: "Gerald Harris", role: "Parent", relationship: "Father of Micah Harris (age 8)" },
        { full_name: "Micah Harris", role: "Child", relationship: "Minor child, age 8" },
        { full_name: "Cheryl Washington", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 8,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-09-0389",
      case_title: "DSS v. Bell — Guardianship",
      case_type: "Guardianship",
      circuit: "Second Judicial Circuit",
      county: "Aiken",
      filed_date: "2023-10-17",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Guardianship case involving Heaven Bell (age 14) and Serenity Bell (age 9). Angela Young completed court-ordered treatment plan including stable housing and random drug screening. Children successfully reunified with Angela Young under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Angela Young", role: "Parent", relationship: "Mother of Heaven Bell (age 14) and Serenity Bell (age 9)" },
        { full_name: "Vernon Bell", role: "Parent", relationship: "Father of Heaven Bell (age 14) and Serenity Bell (age 9)" },
        { full_name: "Heaven Bell", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Serenity Bell", role: "Child", relationship: "Minor child, age 9" },
        { full_name: "Kevin Brooks", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Karen Milford", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 7,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-10-0261",
      case_title: "DSS v. Webb — Emergency Removal",
      case_type: "Emergency Removal",
      circuit: "Seventh Judicial Circuit",
      county: "Spartanburg",
      filed_date: "2023-05-27",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency Removal case involving Faith Webb (age 1). Children removed after children left unsupervised for extended period. William Webb ordered to complete treatment plan including stable housing, random drug screening, substance abuse evaluation and treatment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Patricia Lewis", role: "Parent", relationship: "Mother of Faith Webb (age 1)" },
        { full_name: "William Webb", role: "Parent", relationship: "Father of Faith Webb (age 1)" },
        { full_name: "Faith Webb", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Donna Sullivan", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 7,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-12-0195",
      case_title: "DSS v. Wilson — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Eleventh Judicial Circuit",
      county: "Lexington",
      filed_date: "2023-05-15",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Bryce Wilson (age 1). Nathaniel Wilson completed court-ordered treatment plan including parenting skills classes (12 weeks) and substance abuse evaluation and treatment. Children successfully reunified with Nathaniel Wilson under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Charlene Bell", role: "Parent", relationship: "Mother of Bryce Wilson (age 1)" },
        { full_name: "Nathaniel Wilson", role: "Parent", relationship: "Father of Bryce Wilson (age 1)" },
        { full_name: "Bryce Wilson", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Donna Sullivan", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Patricia Lang", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 6,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-14-0448",
      case_title: "DSS v. Brown — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Fourteenth Judicial Circuit",
      county: "Colleton",
      filed_date: "2024-01-18",
      status: "Dismissed",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Bryce Brown (age 8). Investigation found insufficient evidence to substantiate allegations. Case dismissed by Judge David Strickland.",
      people: [
        { full_name: "Renee Wright", role: "Parent", relationship: "Mother of Bryce Brown (age 8)" },
        { full_name: "Russell Brown", role: "Parent", relationship: "Father of Bryce Brown (age 8)" },
        { full_name: "Bryce Brown", role: "Child", relationship: "Minor child, age 8" },
        { full_name: "David Ortiz", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 8,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-15-0341",
      case_title: "DSS v. Price — Termination of Parental Rights",
      case_type: "Termination of Parental Rights",
      circuit: "Fifth Judicial Circuit",
      county: "Richland",
      filed_date: "2024-02-08",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Petition for termination of parental rights of Crystal Price regarding minor children Amari Price (age 7) and Destiny Price (age 5). Children were removed in August 2023 following substantiated neglect findings. Ms. Price failed to complete court-ordered treatment plan including substance abuse counseling, parenting classes, and stable housing requirements over a 12-month reunification period. Father Brandon Price's rights were voluntarily relinquished in November 2023. Probable cause hearing completed; merits hearing scheduled. Children currently in licensed foster care with pre-adoptive family.",
      people: [
        { full_name: "Crystal Price", role: "Parent", relationship: "Mother of minor children Amari and Destiny Price" },
        { full_name: "Brandon Price", role: "Parent", relationship: "Father of minor children Amari and Destiny Price" },
        { full_name: "Amari Price", role: "Child", relationship: "Minor child, age 7" },
        { full_name: "Destiny Price", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Monica Vance", role: "Case Manager", relationship: "DSS Case Manager assigned August 2023" },
        { full_name: "Dr. Raymond Ellis", role: "Witness", relationship: "Licensed clinical social worker, substance abuse evaluator" },
        { full_name: "Sandra Patterson", role: "Foster Parent", relationship: "Licensed foster parent, pre-adoptive placement" },
        { full_name: "Thomas Reed", role: "Guardian ad Litem", relationship: "Court-appointed GAL for Amari and Destiny Price" }
      ],
      timeline_count: 10,
      statement_count: 12,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-16-0189",
      case_title: "DSS v. Young — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Thirteenth Judicial Circuit",
      county: "Pickens",
      filed_date: "2024-08-08",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving London Young (age 2). Children removed after school reported chronic absenteeism and signs of neglect. Andre Young ordered to complete treatment plan including random drug screening, gainful employment, domestic violence intervention program, individual counseling. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Lorraine Robinson", role: "Parent", relationship: "Mother of London Young (age 2)" },
        { full_name: "Andre Young", role: "Parent", relationship: "Father of London Young (age 2)" },
        { full_name: "London Young", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "Monica Vance", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 7,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-18-0308",
      case_title: "DSS v. Parker — Guardianship",
      case_type: "Guardianship",
      circuit: "Seventh Judicial Circuit",
      county: "Spartanburg",
      filed_date: "2025-01-02",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Guardianship case involving Jalen Parker (age 6) and Maya Parker (age 3). Children removed after parent found to be incapacitated due to substance use while children were present. Robert Parker ordered to complete treatment plan including substance abuse evaluation and treatment, parenting skills classes (12 weeks), stable housing. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Iris Parker", role: "Parent", relationship: "Mother of Jalen Parker (age 6) and Maya Parker (age 3)" },
        { full_name: "Robert Parker", role: "Parent", relationship: "Father of Jalen Parker (age 6) and Maya Parker (age 3)" },
        { full_name: "Jalen Parker", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Maya Parker", role: "Child", relationship: "Minor child, age 3" },
        { full_name: "Lisa Fontaine", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Valerie Dunn", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 6,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-19-0404",
      case_title: "DSS v. Webb — Emergency Removal",
      case_type: "Emergency Removal",
      circuit: "Fifteenth Judicial Circuit",
      county: "Horry",
      filed_date: "2024-05-18",
      status: "Dismissed",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency Removal case involving Kaden Webb (age 9) and Precious Webb (age 14). Investigation found insufficient evidence to substantiate allegations. Case dismissed by Judge Margaret Easley.",
      people: [
        { full_name: "Lakisha Webb", role: "Parent", relationship: "Mother of Kaden Webb (age 9) and Precious Webb (age 14)" },
        { full_name: "Marcus Webb", role: "Parent", relationship: "Father of Kaden Webb (age 9) and Precious Webb (age 14)" },
        { full_name: "Kaden Webb", role: "Child", relationship: "Minor child, age 9" },
        { full_name: "Precious Webb", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Marcus Perry", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Patricia Lang", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 8,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-21-0149",
      case_title: "DSS v. Scott — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Third Judicial Circuit",
      county: "Lee",
      filed_date: "2024-10-09",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Maya Scott (age 10) and Olivia Scott (age 5). Carolyn Scott completed court-ordered treatment plan including anger management classes and psychological evaluation. Children successfully reunified with Carolyn Scott under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Carolyn Scott", role: "Parent", relationship: "Mother of Maya Scott (age 10) and Olivia Scott (age 5)" },
        { full_name: "Anthony Scott", role: "Parent", relationship: "Father of Maya Scott (age 10) and Olivia Scott (age 5)" },
        { full_name: "Maya Scott", role: "Child", relationship: "Minor child, age 10" },
        { full_name: "Olivia Scott", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Derek Lane", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 6,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-21-0325",
      case_title: "DSS v. Harris — Physical Abuse",
      case_type: "Physical Abuse",
      circuit: "Fourteenth Judicial Circuit",
      county: "Allendale",
      filed_date: "2024-03-11",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Physical Abuse case involving Imani Harris (age 6). Rodney Harris completed court-ordered treatment plan including anger management classes and psychological evaluation. Children successfully reunified with Rodney Harris under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Lorraine Harris", role: "Parent", relationship: "Mother of Imani Harris (age 6)" },
        { full_name: "Rodney Harris", role: "Parent", relationship: "Father of Imani Harris (age 6)" },
        { full_name: "Imani Harris", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Tamara Hughes", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 5,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-22-0165",
      case_title: "DSS v. Nelson — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fourth Judicial Circuit",
      county: "Chesterfield",
      filed_date: "2023-04-08",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Faith Nelson (age 8) and Heaven Nelson (age 9). Shonda Nelson completed court-ordered treatment plan including gainful employment and substance abuse evaluation and treatment. Children successfully reunified with Shonda Nelson under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Shonda Nelson", role: "Parent", relationship: "Mother of Faith Nelson (age 8) and Heaven Nelson (age 9)" },
        { full_name: "Darrell Nelson", role: "Parent", relationship: "Father of Faith Nelson (age 8) and Heaven Nelson (age 9)" },
        { full_name: "Faith Nelson", role: "Child", relationship: "Minor child, age 8" },
        { full_name: "Heaven Nelson", role: "Child", relationship: "Minor child, age 9" },
        { full_name: "Sandra Reeves", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Valerie Dunn", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 6,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-24-0413",
      case_title: "DSS v. Moore — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Sixteenth Judicial Circuit",
      county: "Union",
      filed_date: "2023-10-22",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Serenity Moore (age 5). Children removed after sibling disclosed physical abuse to school counselor. William Moore ordered to complete treatment plan including domestic violence intervention program, random drug screening, gainful employment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Diane Moore", role: "Parent", relationship: "Mother of Serenity Moore (age 5)" },
        { full_name: "William Moore", role: "Parent", relationship: "Father of Serenity Moore (age 5)" },
        { full_name: "Serenity Moore", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "David Ortiz", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Philip Crane", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 5,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-24-0502",
      case_title: "DSS v. King — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Twelfth Judicial Circuit",
      county: "Marion",
      filed_date: "2024-04-21",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Aiden King (age 11). Children removed after home found to be unsafe with exposed wiring and no working smoke detectors. Jerome King ordered to complete treatment plan including psychological evaluation, individual counseling, domestic violence intervention program. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Gwendolyn Williams", role: "Parent", relationship: "Mother of Aiden King (age 11)" },
        { full_name: "Jerome King", role: "Parent", relationship: "Father of Aiden King (age 11)" },
        { full_name: "Aiden King", role: "Child", relationship: "Minor child, age 11" },
        { full_name: "Laura Benson", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Philip Crane", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 8,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-25-0177",
      case_title: "DSS v. Green — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Seventh Judicial Circuit",
      county: "Spartanburg",
      filed_date: "2025-03-23",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Bryce Green (age 6). Children removed after parent arrested on drug charges with children in vehicle. Gloria Edwards ordered to complete treatment plan including individual counseling, gainful employment, random drug screening. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Gloria Edwards", role: "Parent", relationship: "Mother of Bryce Green (age 6)" },
        { full_name: "Clarence Green", role: "Parent", relationship: "Father of Bryce Green (age 6)" },
        { full_name: "Bryce Green", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "James Patterson", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-25-0374",
      case_title: "DSS v. Bailey — Emergency Removal",
      case_type: "Emergency Removal",
      circuit: "Sixteenth Judicial Circuit",
      county: "Union",
      filed_date: "2024-08-26",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency Removal case involving Caleb Bailey (age 12). Children removed after parent failed to seek medical attention for child injuries. Corey Bailey ordered to complete treatment plan including substance abuse evaluation and treatment, parenting skills classes (12 weeks), individual counseling, family therapy sessions, gainful employment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Valerie Bailey", role: "Parent", relationship: "Mother of Caleb Bailey (age 12)" },
        { full_name: "Corey Bailey", role: "Parent", relationship: "Father of Caleb Bailey (age 12)" },
        { full_name: "Caleb Bailey", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Donna Sullivan", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 8,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-26-0362",
      case_title: "DSS v. Lewis — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Sixth Judicial Circuit",
      county: "Fairfield",
      filed_date: "2023-04-26",
      status: "Dismissed",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Jalen Lewis (age 6). Investigation found insufficient evidence to substantiate allegations. Case dismissed by Judge Sandra Templeton.",
      people: [
        { full_name: "Felicia Lewis", role: "Parent", relationship: "Mother of Jalen Lewis (age 6)" },
        { full_name: "Travis Lewis", role: "Parent", relationship: "Father of Jalen Lewis (age 6)" },
        { full_name: "Jalen Lewis", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Andrea Foster", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 8,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-26-0373",
      case_title: "DSS v. Rivera — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Fifth Judicial Circuit",
      county: "Kershaw",
      filed_date: "2024-09-15",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Faith Rivera (age 14). Terrence Rivera completed court-ordered treatment plan including psychological evaluation and domestic violence intervention program. Children successfully reunified with Terrence Rivera under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Keisha Rivera", role: "Parent", relationship: "Mother of Faith Rivera (age 14)" },
        { full_name: "Terrence Rivera", role: "Parent", relationship: "Father of Faith Rivera (age 14)" },
        { full_name: "Faith Rivera", role: "Child", relationship: "Minor child, age 14" },
        { full_name: "Donna Sullivan", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Karen Milford", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-26-0425",
      case_title: "DSS v. Baker — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Tenth Judicial Circuit",
      county: "Anderson",
      filed_date: "2025-04-18",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Bryce Baker (age 4). Robert Baker completed court-ordered treatment plan including domestic violence intervention program and parenting skills classes (12 weeks). Children successfully reunified with Robert Baker under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Sonya Webb", role: "Parent", relationship: "Mother of Bryce Baker (age 4)" },
        { full_name: "Robert Baker", role: "Parent", relationship: "Father of Bryce Baker (age 4)" },
        { full_name: "Bryce Baker", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Andrea Foster", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 7,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-28-0275",
      case_title: "DSS v. Hall — Emergency Removal",
      case_type: "Emergency Removal",
      circuit: "Eleventh Judicial Circuit",
      county: "Saluda",
      filed_date: "2024-12-03",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency Removal case involving Jalen Hall (age 1). Clarence Hall completed court-ordered treatment plan including random drug screening and psychological evaluation. Children successfully reunified with Clarence Hall under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Crystal Hall", role: "Parent", relationship: "Mother of Jalen Hall (age 1)" },
        { full_name: "Clarence Hall", role: "Parent", relationship: "Father of Jalen Hall (age 1)" },
        { full_name: "Jalen Hall", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Karen Mitchell", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 5,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-29-0329",
      case_title: "DSS v. Simmons — Emergency Removal",
      case_type: "Emergency Removal",
      circuit: "First Judicial Circuit",
      county: "Calhoun",
      filed_date: "2024-04-12",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency Removal case involving Josiah Simmons (age 3). Lorraine Cox completed court-ordered treatment plan including parenting skills classes (12 weeks) and gainful employment. Children successfully reunified with Lorraine Cox under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Lorraine Cox", role: "Parent", relationship: "Mother of Josiah Simmons (age 3)" },
        { full_name: "Jamal Simmons", role: "Parent", relationship: "Father of Josiah Simmons (age 3)" },
        { full_name: "Josiah Simmons", role: "Child", relationship: "Minor child, age 3" },
        { full_name: "Marcus Perry", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-38-0234",
      case_title: "DSS v. Williams — CPS",
      case_type: "Child Protective Services",
      circuit: "First Judicial Circuit",
      county: "Dorchester",
      filed_date: "2023-12-25",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Protective Services case involving Precious Williams (age 5). Children removed after children found wandering outside at night without supervision. Clarence Williams ordered to complete treatment plan including stable housing, random drug screening, gainful employment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Nicole Williams", role: "Parent", relationship: "Mother of Precious Williams (age 5)" },
        { full_name: "Clarence Williams", role: "Parent", relationship: "Father of Precious Williams (age 5)" },
        { full_name: "Precious Williams", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Donna Sullivan", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Raymond Holt", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 5,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-38-0342",
      case_title: "DSS v. Wright — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fourth Judicial Circuit",
      county: "Marlboro",
      filed_date: "2023-04-26",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Elijah Wright (age 12) and Destiny Wright (age 12). Keisha Wright completed court-ordered treatment plan including domestic violence intervention program and individual counseling. Children successfully reunified with Keisha Wright under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Keisha Wright", role: "Parent", relationship: "Mother of Elijah Wright (age 12) and Destiny Wright (age 12)" },
        { full_name: "Carlos Wright", role: "Parent", relationship: "Father of Elijah Wright (age 12) and Destiny Wright (age 12)" },
        { full_name: "Elijah Wright", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Destiny Wright", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Marcus Perry", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 7,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-40-0436",
      case_title: "DSS v. Baker — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Seventh Judicial Circuit",
      county: "Cherokee",
      filed_date: "2023-08-29",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Malik Baker (age 5). Donovan Baker completed court-ordered treatment plan including psychological evaluation and stable housing. Children successfully reunified with Donovan Baker under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Sabrina Reed", role: "Parent", relationship: "Mother of Malik Baker (age 5)" },
        { full_name: "Donovan Baker", role: "Parent", relationship: "Father of Malik Baker (age 5)" },
        { full_name: "Malik Baker", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Andrea Foster", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 7,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-41-0307",
      case_title: "DSS v. Taylor — Physical Abuse",
      case_type: "Physical Abuse",
      circuit: "Fifth Judicial Circuit",
      county: "Richland",
      filed_date: "2024-08-12",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Physical Abuse case involving Destiny Taylor (age 2). Audrey Taylor completed court-ordered treatment plan including stable housing and family therapy sessions. Children successfully reunified with Audrey Taylor under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Audrey Taylor", role: "Parent", relationship: "Mother of Destiny Taylor (age 2)" },
        { full_name: "Terrence Taylor", role: "Parent", relationship: "Father of Destiny Taylor (age 2)" },
        { full_name: "Destiny Taylor", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "Lisa Fontaine", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Karen Milford", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 7,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-42-0140",
      case_title: "DSS v. Wilson — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Eleventh Judicial Circuit",
      county: "Saluda",
      filed_date: "2024-01-08",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Elijah Wilson (age 4). Children removed after children found wandering outside at night without supervision. Crystal Wilson ordered to complete treatment plan including random drug screening, family therapy sessions, individual counseling, substance abuse evaluation and treatment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Crystal Wilson", role: "Parent", relationship: "Mother of Elijah Wilson (age 4)" },
        { full_name: "Curtis Wilson", role: "Parent", relationship: "Father of Elijah Wilson (age 4)" },
        { full_name: "Elijah Wilson", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Jennifer Tate", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Debra Whitfield", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 6,
      discrepancy_count: 4,
    },
    {
      case_id: "2024-DR-42-0328",
      case_title: "DSS v. Anderson — Guardianship",
      case_type: "Guardianship",
      circuit: "Eighth Judicial Circuit",
      county: "Abbeville",
      filed_date: "2025-06-16",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Guardianship case involving Isaiah Anderson (age 10) and Serenity Anderson (age 1). Sharon Anderson completed court-ordered treatment plan including domestic violence intervention program and random drug screening. Children successfully reunified with Sharon Anderson under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Sharon Anderson", role: "Parent", relationship: "Mother of Isaiah Anderson (age 10) and Serenity Anderson (age 1)" },
        { full_name: "Franklin Anderson", role: "Parent", relationship: "Father of Isaiah Anderson (age 10) and Serenity Anderson (age 1)" },
        { full_name: "Isaiah Anderson", role: "Child", relationship: "Minor child, age 10" },
        { full_name: "Serenity Anderson", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Monica Vance", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Debra Whitfield", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 7,
      discrepancy_count: 2,
    },
    {
      case_id: "2024-DR-42-0424",
      case_title: "DSS v. Taylor — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Third Judicial Circuit",
      county: "Sumter",
      filed_date: "2024-07-08",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Kayla Taylor (age 9). Children removed after home found to be unsafe with exposed wiring and no working smoke detectors. Nicole Wright ordered to complete treatment plan including parenting skills classes (12 weeks), gainful employment, anger management classes, random drug screening. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Nicole Wright", role: "Parent", relationship: "Mother of Kayla Taylor (age 9)" },
        { full_name: "Tyrone Taylor", role: "Parent", relationship: "Father of Kayla Taylor (age 9)" },
        { full_name: "Kayla Taylor", role: "Child", relationship: "Minor child, age 9" },
        { full_name: "Kevin Brooks", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Steven Marsh", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 5,
      discrepancy_count: 3,
    },
    {
      case_id: "2024-DR-42-0892",
      case_title: "DSS v. Webb & Holloway — CPS Emergency Removal",
      case_type: "Child Protective Services",
      circuit: "Seventh Judicial Circuit",
      county: "Spartanburg",
      filed_date: "2024-06-14",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Emergency removal of minor child Jaylen Webb (age 3) following hospital admission for multiple unexplained fractures. Parents Marcus Webb and Dena Holloway provided conflicting accounts of injuries. DSS filed for emergency protective custody. Child placed in kinship foster care with maternal grandmother. Case involves disputed timeline of events, inconsistent parental statements, and medical evidence contradicting both parents accounts.",
      people: [
        { full_name: "Marcus Webb", role: "Parent", relationship: "Father of minor child Jaylen Webb" },
        { full_name: "Dena Holloway", role: "Parent", relationship: "Mother of minor child Jaylen Webb" },
        { full_name: "Jaylen Webb", role: "Child", relationship: "Minor child, age 3" },
        { full_name: "Theresa Holloway", role: "Kinship Foster Parent", relationship: "Maternal grandmother of Jaylen Webb" },
        { full_name: "Renee Dawson", role: "Case Manager", relationship: "DSS Case Manager assigned 2024-06-13" },
        { full_name: "Lt. Frank Odom", role: "Law Enforcement", relationship: "Spartanburg County Sheriff investigator" },
        { full_name: "Dr. Anita Chowdhury", role: "Witness", relationship: "Attending pediatrician, Spartanburg Medical Center" },
        { full_name: "Karen Milford", role: "Guardian ad Litem", relationship: "Court-appointed GAL for Jaylen Webb" }
      ],
      timeline_count: 12,
      statement_count: 15,
      discrepancy_count: 6,
    },
    {
      case_id: "2024-DR-46-0201",
      case_title: "DSS v. Cox — Child Neglect",
      case_type: "Child Neglect",
      circuit: "Eighth Judicial Circuit",
      county: "Abbeville",
      filed_date: "2023-04-16",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Child Neglect case involving Kaden Cox (age 3) and Faith Cox (age 6). Children removed after parent arrested on drug charges with children in vehicle. Bridget Nelson ordered to complete treatment plan including parenting skills classes (12 weeks), gainful employment, substance abuse evaluation and treatment. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Bridget Nelson", role: "Parent", relationship: "Mother of Kaden Cox (age 3) and Faith Cox (age 6)" },
        { full_name: "Wesley Cox", role: "Parent", relationship: "Father of Kaden Cox (age 3) and Faith Cox (age 6)" },
        { full_name: "Kaden Cox", role: "Child", relationship: "Minor child, age 3" },
        { full_name: "Faith Cox", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Brian Colbert", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 5,
      discrepancy_count: 2,
    },
    {
      case_id: "2025-DR-01-0489",
      case_title: "DSS v. Simmons — Family Preservation",
      case_type: "Family Preservation",
      circuit: "Ninth Judicial Circuit",
      county: "Charleston",
      filed_date: "2024-12-26",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Family Preservation case involving Bryce Simmons (age 12) and Olivia Simmons (age 6). Children removed after sibling disclosed physical abuse to school counselor. Clarence Simmons ordered to complete treatment plan including stable housing, domestic violence intervention program, psychological evaluation, individual counseling, random drug screening. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Patricia Moore", role: "Parent", relationship: "Mother of Bryce Simmons (age 12) and Olivia Simmons (age 6)" },
        { full_name: "Clarence Simmons", role: "Parent", relationship: "Father of Bryce Simmons (age 12) and Olivia Simmons (age 6)" },
        { full_name: "Bryce Simmons", role: "Child", relationship: "Minor child, age 12" },
        { full_name: "Olivia Simmons", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "David Ortiz", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Patricia Lang", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 8,
      discrepancy_count: 4,
    },
    {
      case_id: "2025-DR-06-0246",
      case_title: "DSS v. Morris — Guardianship",
      case_type: "Guardianship",
      circuit: "Fourteenth Judicial Circuit",
      county: "Colleton",
      filed_date: "2024-06-23",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Guardianship case involving Ebony Morris (age 8) and Terrell Morris (age 4). Vernon Morris completed court-ordered treatment plan including substance abuse evaluation and treatment and anger management classes. Children successfully reunified with Vernon Morris under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Denise Morris", role: "Parent", relationship: "Mother of Ebony Morris (age 8) and Terrell Morris (age 4)" },
        { full_name: "Vernon Morris", role: "Parent", relationship: "Father of Ebony Morris (age 8) and Terrell Morris (age 4)" },
        { full_name: "Ebony Morris", role: "Child", relationship: "Minor child, age 8" },
        { full_name: "Terrell Morris", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Derek Lane", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Howard Grant", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 6,
      discrepancy_count: 2,
    },
    {
      case_id: "2025-DR-07-0448",
      case_title: "DSS v. Morris — Physical Abuse",
      case_type: "Physical Abuse",
      circuit: "Fifteenth Judicial Circuit",
      county: "Horry",
      filed_date: "2025-05-06",
      status: "Closed",
      plaintiff: "SC Department of Social Services",
      summary: "Physical Abuse case involving Diamond Morris (age 5) and Ebony Morris (age 1). Rhonda Morris completed court-ordered treatment plan including stable housing and family therapy sessions. Children successfully reunified with Rhonda Morris under ongoing DSS monitoring. Case closed.",
      people: [
        { full_name: "Rhonda Morris", role: "Parent", relationship: "Mother of Diamond Morris (age 5) and Ebony Morris (age 1)" },
        { full_name: "Donovan Morris", role: "Parent", relationship: "Father of Diamond Morris (age 5) and Ebony Morris (age 1)" },
        { full_name: "Diamond Morris", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Ebony Morris", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "David Ortiz", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Thomas Reed", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 8,
      discrepancy_count: 3,
    },
    {
      case_id: "2025-DR-09-0443",
      case_title: "DSS v. Reed — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fourth Judicial Circuit",
      county: "Dillon",
      filed_date: "2023-11-17",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Micah Reed (age 5). Children removed after home found to be unsafe with exposed wiring and no working smoke detectors. Diane Jackson ordered to complete treatment plan including substance abuse evaluation and treatment, individual counseling, parenting skills classes (12 weeks), random drug screening, anger management classes. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Diane Jackson", role: "Parent", relationship: "Mother of Micah Reed (age 5)" },
        { full_name: "Robert Reed", role: "Parent", relationship: "Father of Micah Reed (age 5)" },
        { full_name: "Micah Reed", role: "Child", relationship: "Minor child, age 5" },
        { full_name: "Brian Colbert", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Caroline Fisher", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 7,
      statement_count: 8,
      discrepancy_count: 2,
    },
    {
      case_id: "2025-DR-21-0289",
      case_title: "DSS v. Parker — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fifth Judicial Circuit",
      county: "Richland",
      filed_date: "2023-06-04",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Jaylen Parker (age 6). Children removed after home environment found to be unsanitary with animal waste and spoiled food. Eric Parker ordered to complete treatment plan including domestic violence intervention program, parenting skills classes (12 weeks), family therapy sessions, psychological evaluation. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Valerie Lewis", role: "Parent", relationship: "Mother of Jaylen Parker (age 6)" },
        { full_name: "Eric Parker", role: "Parent", relationship: "Father of Jaylen Parker (age 6)" },
        { full_name: "Jaylen Parker", role: "Child", relationship: "Minor child, age 6" },
        { full_name: "Kevin Brooks", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Raymond Holt", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 5,
      statement_count: 6,
      discrepancy_count: 4,
    },
    {
      case_id: "2025-DR-24-0382",
      case_title: "DSS v. Young — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fifth Judicial Circuit",
      county: "Kershaw",
      filed_date: "2024-10-05",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Aiden Young (age 4). Children removed after children left unsupervised for extended period. Nathaniel Young ordered to complete treatment plan including substance abuse evaluation and treatment, domestic violence intervention program, psychological evaluation. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Bridget Young", role: "Parent", relationship: "Mother of Aiden Young (age 4)" },
        { full_name: "Nathaniel Young", role: "Parent", relationship: "Father of Aiden Young (age 4)" },
        { full_name: "Aiden Young", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Sandra Reeves", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Natalie Voss", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 6,
      discrepancy_count: 4,
    },
    {
      case_id: "2025-DR-31-0446",
      case_title: "DSS v. Allen — Voluntary Placement",
      case_type: "Voluntary Placement",
      circuit: "Sixth Judicial Circuit",
      county: "Lancaster",
      filed_date: "2024-04-02",
      status: "Active",
      plaintiff: "SC Department of Social Services",
      summary: "Voluntary Placement case involving Chloe Allen (age 2) and Terrell Allen (age 1). Children removed after children left unsupervised for extended period. Tonya Walker ordered to complete treatment plan including gainful employment, stable housing, psychological evaluation. Case is ongoing with next hearing scheduled.",
      people: [
        { full_name: "Tonya Walker", role: "Parent", relationship: "Mother of Chloe Allen (age 2) and Terrell Allen (age 1)" },
        { full_name: "Franklin Allen", role: "Parent", relationship: "Father of Chloe Allen (age 2) and Terrell Allen (age 1)" },
        { full_name: "Chloe Allen", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "Terrell Allen", role: "Child", relationship: "Minor child, age 1" },
        { full_name: "Marcus Perry", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Philip Crane", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 8,
      statement_count: 8,
      discrepancy_count: 2,
    },
    {
      case_id: "2025-DR-45-0184",
      case_title: "DSS v. Morris — TPR",
      case_type: "Termination of Parental Rights",
      circuit: "Fifth Judicial Circuit",
      county: "Richland",
      filed_date: "2023-05-14",
      status: "Dismissed",
      plaintiff: "SC Department of Social Services",
      summary: "Termination of Parental Rights case involving Nia Morris (age 4) and Devonte Morris (age 2). Investigation found insufficient evidence to substantiate allegations. Case dismissed by Judge Harold Wynn.",
      people: [
        { full_name: "Deborah Morris", role: "Parent", relationship: "Mother of Nia Morris (age 4) and Devonte Morris (age 2)" },
        { full_name: "Mitchell Morris", role: "Parent", relationship: "Father of Nia Morris (age 4) and Devonte Morris (age 2)" },
        { full_name: "Nia Morris", role: "Child", relationship: "Minor child, age 4" },
        { full_name: "Devonte Morris", role: "Child", relationship: "Minor child, age 2" },
        { full_name: "Jennifer Tate", role: "Case Manager", relationship: "DSS Case Manager" },
        { full_name: "Thomas Reed", role: "Guardian ad Litem", relationship: "Court-appointed GAL" }
      ],
      timeline_count: 6,
      statement_count: 7,
      discrepancy_count: 2,
    }
  ];

  // ---- Render Case List ----
  function renderCaseList(cases) {
    casesData = cases;

    const html = `
      <table class="case-table">
        <thead>
          <tr>
            <th>Case ID</th>
            <th>Title</th>
            <th>Type</th>
            <th>County</th>
            <th>Filed</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${cases
            .map(
              (c) => `
            <tr>
              <td class="clickable" data-case-id="${c.case_id}">${c.case_id}</td>
              <td>${c.case_title}</td>
              <td>${c.case_type}</td>
              <td>${c.county}</td>
              <td>${c.filed_date}</td>
              <td><span class="status-badge ${c.status.toLowerCase()}">${c.status}</span></td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    `;

    caseListEl.innerHTML = html;

    // Click handlers for case IDs
    caseListEl.querySelectorAll(".clickable").forEach((el) => {
      el.addEventListener("click", () => {
        const caseId = el.getAttribute("data-case-id");
        showCaseDetail(caseId);
      });
    });
  }

  // ---- Render Case Detail ----
  function showCaseDetail(caseId) {
    const caseData = casesData.find((c) => c.case_id === caseId);
    if (!caseData) return;

    caseListEl.style.display = "none";
    caseDetailEl.style.display = "block";

    const peopleRows = (caseData.people || [])
      .map(
        (p) => `
        <tr>
          <td>${p.full_name}</td>
          <td>${p.role}</td>
          <td>${p.relationship || ""}</td>
        </tr>
      `
      )
      .join("");

    caseDetailEl.innerHTML = `
      <div class="case-detail">
        <button class="back-btn" id="backToList">&larr; Back to cases</button>
        <h3>${caseData.case_title}</h3>

        <div class="detail-grid">
          <div class="label">Case ID</div><div>${caseData.case_id}</div>
          <div class="label">Type</div><div>${caseData.case_type}</div>
          <div class="label">Circuit</div><div>${caseData.circuit}</div>
          <div class="label">County</div><div>${caseData.county}</div>
          <div class="label">Filed</div><div>${caseData.filed_date}</div>
          <div class="label">Status</div><div><span class="status-badge ${caseData.status.toLowerCase()}">${caseData.status}</span></div>
          <div class="label">Plaintiff</div><div>${caseData.plaintiff}</div>
        </div>

        <p>${caseData.summary}</p>

        <div class="stat-cards">
          <div class="stat-card">
            <div class="number">${caseData.timeline_count || "—"}</div>
            <div class="label">Timeline Events</div>
          </div>
          <div class="stat-card">
            <div class="number">${caseData.statement_count || "—"}</div>
            <div class="label">Statements</div>
          </div>
          <div class="stat-card">
            <div class="number">${caseData.discrepancy_count || "—"}</div>
            <div class="label">Discrepancies</div>
          </div>
        </div>

        <div class="detail-section">
          <h4>People</h4>
          <table class="case-table">
            <thead>
              <tr><th>Name</th><th>Role</th><th>Relationship</th></tr>
            </thead>
            <tbody>${peopleRows}</tbody>
          </table>
        </div>
      </div>
    `;

    document.getElementById("backToList").addEventListener("click", () => {
      caseDetailEl.style.display = "none";
      caseListEl.style.display = "block";
    });
  }

  // ---- Load Cases ----
  async function loadCases() {
    // Use embedded data for the demo — no API dependency for the browser panel
    renderCaseList(EMBEDDED_CASES);
  }

  return { loadCases };
})();
