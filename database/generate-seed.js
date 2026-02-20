/**
 * Generates seed.sql with 50 realistic synthetic DSS cases.
 * Cases 1-2 are hand-crafted demo cases (written inline).
 * Cases 3-50 are procedurally generated with realistic variety.
 *
 * Usage: node generate-seed.js > seed-generated.sql
 */

const CASE_TYPES = [
  'Child Protective Services',
  'Termination of Parental Rights',
  'Child Neglect',
  'Physical Abuse',
  'Emergency Removal',
  'Voluntary Placement',
  'Guardianship',
  'Family Preservation',
];

const STATUSES = ['Active', 'Active', 'Active', 'Closed', 'Closed', 'Dismissed'];

const CIRCUITS = [
  { circuit: 'First Judicial Circuit', counties: ['Calhoun', 'Dorchester', 'Orangeburg'] },
  { circuit: 'Second Judicial Circuit', counties: ['Aiken', 'Bamberg', 'Barnwell'] },
  { circuit: 'Third Judicial Circuit', counties: ['Clarendon', 'Lee', 'Sumter', 'Williamsburg'] },
  { circuit: 'Fourth Judicial Circuit', counties: ['Chesterfield', 'Darlington', 'Dillon', 'Marlboro'] },
  { circuit: 'Fifth Judicial Circuit', counties: ['Kershaw', 'Richland'] },
  { circuit: 'Sixth Judicial Circuit', counties: ['Chester', 'Fairfield', 'Lancaster'] },
  { circuit: 'Seventh Judicial Circuit', counties: ['Cherokee', 'Spartanburg'] },
  { circuit: 'Eighth Judicial Circuit', counties: ['Abbeville', 'Greenwood', 'Laurens', 'Newberry'] },
  { circuit: 'Ninth Judicial Circuit', counties: ['Berkeley', 'Charleston'] },
  { circuit: 'Tenth Judicial Circuit', counties: ['Anderson', 'Oconee'] },
  { circuit: 'Eleventh Judicial Circuit', counties: ['Edgefield', 'Lexington', 'McCormick', 'Saluda'] },
  { circuit: 'Twelfth Judicial Circuit', counties: ['Florence', 'Marion'] },
  { circuit: 'Thirteenth Judicial Circuit', counties: ['Greenville', 'Pickens'] },
  { circuit: 'Fourteenth Judicial Circuit', counties: ['Allendale', 'Beaufort', 'Colleton', 'Hampton', 'Jasper'] },
  { circuit: 'Fifteenth Judicial Circuit', counties: ['Georgetown', 'Horry'] },
  { circuit: 'Sixteenth Judicial Circuit', counties: ['Union', 'York'] },
];

const FIRST_NAMES_M = ['Marcus', 'Tyrone', 'Devon', 'James', 'Carlos', 'Andre', 'Robert', 'William', 'Kevin', 'Brian',
  'Terrence', 'Dwayne', 'Jerome', 'Anthony', 'Michael', 'Christopher', 'Darius', 'Lamar', 'Jamal', 'Travis',
  'Rodney', 'Curtis', 'Donovan', 'Reginald', 'Clarence', 'Wesley', 'Franklin', 'Clifton', 'Vernon', 'Nathaniel',
  'Gerald', 'Raymond', 'Eric', 'Darrell', 'Corey', 'Mitchell', 'Clayton', 'Russell', 'Cedric', 'Glen'];

const FIRST_NAMES_F = ['Dena', 'Crystal', 'Tasha', 'Keisha', 'Latoya', 'Jasmine', 'Nicole', 'Brenda', 'Tamika', 'Shonda',
  'Monique', 'Alicia', 'Tonya', 'Angela', 'Denise', 'Patricia', 'Sharon', 'Vanessa', 'Yolanda', 'Felicia',
  'Wanda', 'Rhonda', 'Lakisha', 'Charlene', 'Deborah', 'Cynthia', 'Gloria', 'Tiffany', 'Sonya', 'Carolyn',
  'Diane', 'Renee', 'Bridget', 'Lorraine', 'Valerie', 'Nadine', 'Sabrina', 'Audrey', 'Gwendolyn', 'Iris'];

const LAST_NAMES = ['Webb', 'Holloway', 'Price', 'Simmons', 'Jackson', 'Williams', 'Brown', 'Davis', 'Wilson', 'Moore',
  'Taylor', 'Anderson', 'Thomas', 'Harris', 'Robinson', 'Clark', 'Lewis', 'Walker', 'Hall', 'Young',
  'Allen', 'King', 'Wright', 'Scott', 'Green', 'Baker', 'Adams', 'Nelson', 'Carter', 'Mitchell',
  'Perez', 'Campbell', 'Parker', 'Edwards', 'Collins', 'Stewart', 'Morris', 'Rogers', 'Reed', 'Cook',
  'Morgan', 'Bell', 'Murphy', 'Bailey', 'Rivera', 'Cooper', 'Richardson', 'Cox', 'Howard', 'Ward'];

const CHILD_NAMES_M = ['Jaylen', 'Amari', 'Malik', 'Devonte', 'Isaiah', 'Elijah', 'Noah', 'Caleb', 'Josiah', 'Micah',
  'Zion', 'Bryce', 'Kaden', 'Jalen', 'Terrell', 'Deshawn', 'Aiden', 'Liam', 'Xavier', 'Tyree'];

const CHILD_NAMES_F = ['Destiny', 'Keyana', 'Aaliyah', 'Brianna', 'Chloe', 'Diamond', 'Ebony', 'Faith', 'Gabrielle', 'Heaven',
  'Imani', 'Janiya', 'Kayla', 'London', 'Maya', 'Nia', 'Olivia', 'Precious', 'Raven', 'Serenity'];

const CM_NAMES = ['Renee Dawson', 'Monica Vance', 'David Ortiz', 'Lisa Fontaine', 'Karen Mitchell', 'James Patterson',
  'Sandra Reeves', 'Tamara Hughes', 'Kevin Brooks', 'Andrea Foster', 'Marcus Perry', 'Donna Sullivan',
  'Robert Simms', 'Jennifer Tate', 'Brian Colbert', 'Cheryl Washington', 'Derek Lane', 'Laura Benson'];

const GAL_NAMES = ['Karen Milford', 'Thomas Reed', 'Patricia Lang', 'Howard Grant', 'Debra Whitfield', 'Steven Marsh',
  'Caroline Fisher', 'Raymond Holt', 'Valerie Dunn', 'Gregory Blake', 'Natalie Voss', 'Philip Crane'];

const JUDGE_NAMES = ['Judge Margaret Easley', 'Judge Harold Wynn', 'Judge Sandra Templeton', 'Judge Robert Faircloth',
  'Judge Diane Crawford', 'Judge William Harmon', 'Judge Theresa Boyd', 'Judge Kenneth Fulton',
  'Judge Carolyn Bridges', 'Judge David Strickland'];

const INJURY_TYPES = [
  'bruising on arms and torso inconsistent with reported fall',
  'spiral fracture of the left tibia',
  'multiple contusions at different stages of healing',
  'burn marks on both hands consistent with contact burn',
  'subdural hematoma identified on CT scan',
  'malnutrition and failure to thrive',
  'untreated dental infections and severe tooth decay',
  'healing rib fractures visible on chest X-ray',
  'lacerations requiring sutures on forehead',
  'severe diaper rash and skin breakdown indicating prolonged neglect',
];

const REMOVAL_REASONS = [
  'home found to be unsafe with exposed wiring and no working smoke detectors',
  'children left unsupervised for extended period',
  'parent found to be incapacitated due to substance use while children were present',
  'domestic violence incident witnessed by children',
  'parent failed to seek medical attention for child injuries',
  'children found wandering outside at night without supervision',
  'home environment found to be unsanitary with animal waste and spoiled food',
  'parent arrested on drug charges with children in vehicle',
  'school reported chronic absenteeism and signs of neglect',
  'sibling disclosed physical abuse to school counselor',
];

const TREATMENT_ITEMS = [
  'substance abuse evaluation and treatment',
  'parenting skills classes (12 weeks)',
  'individual counseling',
  'domestic violence intervention program',
  'anger management classes',
  'random drug screening',
  'stable housing',
  'gainful employment',
  'psychological evaluation',
  'family therapy sessions',
];

const EVENT_TYPES = ['Medical', 'Court', 'DSS Action', 'Law Enforcement', 'Family', 'Placement'];

const DOC_TYPES = ['Dictation PDF', 'Court Filing', 'Medical Records', 'Sheriff Report', 'Home Visit Report',
  'Court Transcript', 'DSS Intake Report', 'Placement Agreement', 'GAL Report', 'School Report',
  'Drug Screen Report', 'Psychological Evaluation', 'Treatment Progress Report'];

let personIdCounter = 0;
let eventIdCounter = 0;
let statementIdCounter = 0;
let discrepancyIdCounter = 0;

function esc(str) {
  return str.replace(/'/g, "''");
}

function pick(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function pickN(arr, n) {
  const shuffled = [...arr].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, n);
}

function randomDate(startYear, startMonth, endYear, endMonth) {
  const start = new Date(startYear, startMonth - 1, 1);
  const end = new Date(endYear, endMonth - 1, 28);
  const d = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return d.toISOString().split('T')[0];
}

function randomDob(minAge, maxAge) {
  const now = new Date(2024, 6, 1);
  const age = minAge + Math.random() * (maxAge - minAge);
  const dob = new Date(now.getTime() - age * 365.25 * 24 * 60 * 60 * 1000);
  return dob.toISOString().split('T')[0];
}

function randomTime() {
  const hours = Math.floor(Math.random() * 12) + 1;
  const mins = pick(['00', '15', '30', '45']);
  const ampm = pick(['AM', 'PM']);
  return `${hours}:${mins} ${ampm}`;
}

function generateCaseId(index) {
  const year = pick(['2023', '2024', '2024', '2024', '2025']);
  const circuit = String(Math.floor(Math.random() * 46) + 1).padStart(2, '0');
  const seq = String(index * 7 + Math.floor(Math.random() * 100) + 100).padStart(4, '0');
  return `${year}-DR-${circuit}-${seq}`;
}

function generateCase(caseId, idx) {
  const circuitInfo = pick(CIRCUITS);
  const county = pick(circuitInfo.counties);
  const caseType = pick(CASE_TYPES);
  const status = pick(STATUSES);
  const filedDate = randomDate(2023, 3, 2025, 6);

  // Generate family
  const motherFirst = pick(FIRST_NAMES_F);
  const fatherFirst = pick(FIRST_NAMES_M);
  const familyLast = pick(LAST_NAMES);
  const motherLast = Math.random() > 0.5 ? familyLast : pick(LAST_NAMES);
  const motherName = `${motherFirst} ${motherLast}`;
  const fatherName = `${fatherFirst} ${familyLast}`;

  const numChildren = Math.random() > 0.6 ? 2 : 1;
  const children = [];
  for (let c = 0; c < numChildren; c++) {
    const childFirst = c === 0
      ? (Math.random() > 0.5 ? pick(CHILD_NAMES_M) : pick(CHILD_NAMES_F))
      : (Math.random() > 0.5 ? pick(CHILD_NAMES_M) : pick(CHILD_NAMES_F));
    const childAge = Math.floor(Math.random() * 14) + 1;
    children.push({ name: `${childFirst} ${familyLast}`, age: childAge, dob: randomDob(childAge, childAge + 1) });
  }

  const childrenDesc = children.map(c => `${c.name} (age ${c.age})`).join(' and ');
  const cmName = pick(CM_NAMES);
  const galName = pick(GAL_NAMES);
  const judgeName = pick(JUDGE_NAMES);

  const removalReason = pick(REMOVAL_REASONS);
  const injury = pick(INJURY_TYPES);
  const treatments = pickN(TREATMENT_ITEMS, 3 + Math.floor(Math.random() * 3));

  const defendant = Math.random() > 0.4 ? motherName : fatherName;
  const otherParent = defendant === motherName ? fatherName : motherName;

  const titleSuffix = caseType === 'Termination of Parental Rights' ? 'TPR'
    : caseType === 'Child Protective Services' ? 'CPS'
    : caseType === 'Emergency Removal' ? 'Emergency Removal'
    : caseType;

  const caseTitle = `DSS v. ${familyLast} — ${titleSuffix}`;

  const summary = status === 'Closed'
    ? `${caseType} case involving ${childrenDesc}. ${defendant} completed court-ordered treatment plan including ${treatments.slice(0, 2).join(' and ')}. Children successfully reunified with ${defendant} under ongoing DSS monitoring. Case closed.`
    : status === 'Dismissed'
    ? `${caseType} case involving ${childrenDesc}. Investigation found insufficient evidence to substantiate allegations. Case dismissed by ${judgeName}.`
    : `${caseType} case involving ${childrenDesc}. Children removed after ${removalReason}. ${defendant} ordered to complete treatment plan including ${treatments.join(', ')}. Case is ongoing with next hearing scheduled.`;

  const sql = [];

  // Case INSERT
  sql.push(`INSERT INTO cases (case_id, case_title, case_type, circuit, county, filed_date, status, plaintiff, summary) VALUES ('${caseId}', '${esc(caseTitle)}', '${esc(caseType)}', '${esc(circuitInfo.circuit)}', '${esc(county)}', '${filedDate}', '${status}', 'SC Department of Social Services', '${esc(summary)}');`);

  // People
  const people = [];
  const motherPid = ++personIdCounter;
  people.push({ pid: motherPid, name: motherName, role: 'Parent', rel: `Mother of ${childrenDesc}` });
  sql.push(`INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES ('${caseId}', '${esc(motherName)}', 'Parent', 'Mother of ${esc(childrenDesc)}', '${randomDob(25, 40)}', NULL);`);

  const fatherPid = ++personIdCounter;
  people.push({ pid: fatherPid, name: fatherName, role: 'Parent', rel: `Father of ${childrenDesc}` });
  sql.push(`INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES ('${caseId}', '${esc(fatherName)}', 'Parent', 'Father of ${esc(childrenDesc)}', '${randomDob(25, 42)}', NULL);`);

  const childPids = [];
  for (const child of children) {
    const cpid = ++personIdCounter;
    childPids.push(cpid);
    people.push({ pid: cpid, name: child.name, role: 'Child', rel: `Minor child, age ${child.age}` });
    sql.push(`INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES ('${caseId}', '${esc(child.name)}', 'Child', 'Minor child, age ${child.age}', '${child.dob}', NULL);`);
  }

  const cmPid = ++personIdCounter;
  people.push({ pid: cmPid, name: cmName, role: 'Case Manager' });
  sql.push(`INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES ('${caseId}', '${esc(cmName)}', 'Case Manager', 'DSS Case Manager', NULL, NULL);`);

  const galPid = ++personIdCounter;
  people.push({ pid: galPid, name: galName, role: 'Guardian ad Litem' });
  sql.push(`INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES ('${caseId}', '${esc(galName)}', 'Guardian ad Litem', 'Court-appointed GAL', NULL, NULL);`);

  // Timeline events (5-8 per case)
  const numEvents = 5 + Math.floor(Math.random() * 4);
  const baseDate = new Date(filedDate);
  const eventDates = [];
  for (let i = 0; i < numEvents; i++) {
    const d = new Date(baseDate.getTime() + (i - 2) * (7 + Math.random() * 14) * 86400000);
    eventDates.push(d.toISOString().split('T')[0]);
  }
  eventDates.sort();

  const eventTemplates = [
    { type: 'DSS Action', desc: `DSS receives referral regarding ${children[0].name}. ${pick(['School reports', 'Hospital reports', 'Neighbor reports', 'Anonymous tipline reports'])} concerns about ${pick(['child welfare', 'home conditions', 'suspected abuse', 'suspected neglect'])}.`, doc: 'DSS Intake Report', parties: `${children[0].name}, ${cmName}` },
    { type: 'DSS Action', desc: `${cmName} conducts ${pick(['unannounced', 'scheduled'])} home visit. Finds ${removalReason}. ${defendant} ${pick(['cooperative but defensive', 'uncooperative and hostile', 'not present at the home', 'appeared impaired'])}.`, doc: 'Home Visit Report', parties: `${cmName}, ${defendant}` },
    { type: 'DSS Action', desc: `DSS obtains emergency removal order. ${childrenDesc} placed in ${pick(['emergency foster care', 'kinship care with relative', 'temporary shelter care'])}. ${defendant} informed of removal and rights.`, doc: 'Court Filing, Emergency Order', parties: `${cmName}, ${defendant}, ${childrenDesc}` },
    { type: 'Court', desc: `Probable cause hearing before ${judgeName}. Court finds probable cause of ${caseType.toLowerCase().includes('neglect') ? 'neglect' : 'abuse'}. ${defendant} present with ${pick(['appointed', 'retained'])} counsel. Treatment plan ordered: ${treatments.join(', ')}.`, doc: 'Court Filing, Order 1', parties: `${defendant}, ${cmName}, ${judgeName}` },
    { type: 'Court', desc: `Review hearing. ${defendant} has ${pick(['made minimal progress', 'shown some improvement', 'not complied with', 'partially completed'])} on court-ordered treatment plan. ${pick(['Court continues current orders.', 'Court warns of potential TPR.', 'Court schedules merits hearing.', 'Court approves modified case plan.'])}`, doc: 'Court Filing, Order 2', parties: `${defendant}, ${cmName}, ${judgeName}` },
    { type: 'Placement', desc: `${childrenDesc} ${pick(['placed with licensed foster family', 'transferred to kinship placement', 'placed in therapeutic foster care', 'moved to pre-adoptive placement'])}.`, doc: 'Placement Agreement', parties: `${childrenDesc}, ${cmName}` },
    { type: 'Medical', desc: `${pick(['Medical examination', 'Psychological evaluation', 'Substance abuse evaluation', 'Forensic interview'])} of ${pick([defendant, children[0].name])} completed. ${pick(['Results pending.', 'Findings consistent with reported concerns.', 'No acute findings at this time.', 'Referral for additional services recommended.'])}`, doc: pick(['Medical Records', 'Psychological Evaluation', 'Substance Abuse Evaluation Report']), parties: pick([defendant, children[0].name]) },
    { type: 'Law Enforcement', desc: `${pick(['Sheriff deputy', 'Police officer', 'Detective'])} ${pick(['responds to home', 'interviews witnesses', 'takes report', 'serves protective order'])}. ${pick(['No arrest made at this time.', 'Incident documented for DSS coordination.', 'Charges filed pending investigation.', 'Referred to family court.'])}`, doc: 'Sheriff Report', parties: `${defendant}, ${otherParent}` },
    { type: 'DSS Action', desc: `${cmName} conducts follow-up visit. ${pick(['Children appear to be adjusting well in placement.', 'Supervised visitation occurring as scheduled.', 'Parent has not attended scheduled visitation.', 'Home conditions have improved since last visit.'])}`, doc: 'Dictation PDF', parties: `${cmName}, ${defendant}` },
    { type: 'Court', desc: `${pick(['Merits hearing', 'Permanency hearing', 'Status conference', 'Motion hearing'])} held. ${pick(['Case continued for further review.', 'Court orders permanency plan.', 'DSS recommends continued placement.', 'Parent requests additional time to comply.'])}`, doc: 'Court Transcript', parties: `${defendant}, ${cmName}, ${judgeName}, ${galName}` },
  ];

  for (let i = 0; i < numEvents; i++) {
    const tmpl = eventTemplates[i % eventTemplates.length];
    const time = Math.random() > 0.3 ? `'${randomTime()}'` : 'NULL';
    const page = `p. ${Math.floor(Math.random() * 30) + 1}`;
    sql.push(`INSERT INTO timeline_events (case_id, event_date, event_time, event_type, description, source_document, parties_involved) VALUES ('${caseId}', '${eventDates[i]}', ${time}, '${tmpl.type}', '${esc(tmpl.desc)}', '${esc(tmpl.doc)}, ${page}', '${esc(tmpl.parties)}');`);
  }

  // Statements (5-8 per case)
  const numStatements = 5 + Math.floor(Math.random() * 4);
  const statementSources = ['Case Manager', 'Court', 'Law Enforcement', 'Medical Staff'];
  const defStatements = [
    `I love my ${pick(['children', 'kids', 'babies'])}. I would never hurt them. ${pick(['I just need some help.', 'Things have been hard.', 'I am doing my best.', 'I know I made mistakes.'])}`,
    `I am ${pick(['clean now', 'working on myself', 'going to my appointments', 'getting my life together'])}. I ${pick(['just need more time', 'want my kids back', 'am willing to do whatever it takes', 'have been following the case plan'])}`,
    `${pick(['That is not what happened.', 'The report is not accurate.', 'I was not there when that happened.', 'They are exaggerating.'])} ${pick(['I can explain.', 'It was a misunderstanding.', 'The kids were never in danger.', 'Someone else was responsible.'])}`,
    `I have been going to ${pick(['my classes', 'counseling', 'NA meetings', 'therapy'])} ${pick(['every week', 'when I can', 'regularly', 'since the court ordered it'])}. ${pick(['I have the certificates.', 'My counselor can confirm.', 'I have not missed any.', 'Transportation has been difficult.'])}`,
    `${pick(['I understand what DSS is asking.', 'I know the children need to be safe.', 'I accept responsibility.', 'I want to work with the court.'])} ${pick(['I am a good parent.', 'I can provide a safe home.', 'I have made changes.', 'Things are different now.'])}`,
  ];

  const cmStatements = [
    `During my ${pick(['initial assessment', 'home visit', 'follow-up visit', 'office interview'])}, ${defendant} ${pick(['was cooperative but appeared anxious', 'was hostile and refused to answer questions', 'minimized the severity of the situation', 'appeared to be under the influence'])}. ${pick(['The home was not safe for children.', 'I have concerns about the children returning.', 'Compliance with the case plan has been minimal.', 'Progress has been made but is insufficient.'])}`,
    `${defendant} has ${pick(['attended', 'missed', 'partially completed', 'not enrolled in'])} ${pick(['3 of 12', '1 of 8', '5 of 12', '7 of 12'])} required ${pick(['treatment sessions', 'parenting classes', 'counseling appointments', 'drug screens'])}. ${pick(['This level of compliance is insufficient.', 'DSS continues to monitor.', 'Additional supports have been offered.', 'We recommend continued out-of-home placement.'])}`,
    `I ${pick(['visited the children', 'spoke with the foster family', 'observed supervised visitation', 'reviewed school records'])} on ${randomDate(2024, 1, 2025, 3)}. ${pick(['The children are adjusting well.', 'There are behavioral concerns.', 'The children expressed desire to return home.', 'The placement is stable and appropriate.'])}`,
  ];

  const galStatements = [
    `In my assessment, ${pick(['the children are thriving in their current placement', 'it is in the best interest of the children to remain in care', 'the parent has not demonstrated ability to provide safe care', 'further time is needed to evaluate reunification potential'])}. I recommend ${pick(['continued out-of-home placement', 'TPR and adoption planning', 'reunification with safety plan', 'a permanency hearing be scheduled'])}.`,
  ];

  for (let i = 0; i < numStatements; i++) {
    let pid, text, madeTo, doc;
    if (i < 3) {
      // Defendant statements
      pid = defendant === motherName ? motherPid : fatherPid;
      text = defStatements[i % defStatements.length];
      madeTo = pick(statementSources);
      doc = pick(['Dictation PDF', 'Court Transcript', 'Sheriff Report']);
    } else if (i < numStatements - 1) {
      // Case manager statements
      pid = cmPid;
      text = cmStatements[i % cmStatements.length];
      madeTo = pick(['Court', 'Case Manager']);
      doc = pick(['Dictation PDF', 'Court Transcript', 'Home Visit Report']);
    } else {
      // GAL statement
      pid = galPid;
      text = galStatements[0];
      madeTo = 'Court';
      doc = 'GAL Report';
    }
    const stmtDate = eventDates[Math.min(i, eventDates.length - 1)];
    const page = `p. ${Math.floor(Math.random() * 25) + 1}`;
    sql.push(`INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES ('${caseId}', ${pid}, '${stmtDate}', '${madeTo}', '${esc(text)}', '${esc(doc)}', '${page}');`);
  }

  // Discrepancies (2-4 per case)
  const numDisc = 2 + Math.floor(Math.random() * 3);
  const discTopics = [
    { topic: 'Cause of injuries / incident', aAcct: `States the ${pick(['child fell', 'injuries were accidental', 'incident did not happen', 'child was already hurt'])}. ${pick(['Claims no knowledge of how injuries occurred.', 'Blames the other parent.', 'Says child was injured at school/daycare.', 'Reports child fell from furniture.'])}`, bAcct: `${pick(['Medical evidence', 'Other parent', 'Witness account', 'Physical evidence'])} contradicts this account. ${pick(['Injuries inconsistent with reported mechanism.', 'Witness observed different events.', 'Timeline does not support claim.', 'Other parent provides conflicting version.'])}`, contra: `${pick(['Medical records', 'Witness statement', 'Physical evidence', 'Other parent testimony'])} contradicts this account.` },
    { topic: 'Home conditions', aAcct: `States the home is ${pick(['clean and safe', 'adequate for the children', 'being improved', 'temporarily messy due to moving'])}. Denies any safety hazards.`, bAcct: `${cmName} documents ${pick(['unsanitary conditions', 'safety hazards', 'lack of food', 'utility shutoffs', 'exposed wiring'])} during home visit. ${pick(['Photographs taken.', 'Conditions verified by law enforcement.', 'Multiple visits confirmed issues.'])}`, contra: `Home visit report and photographs contradict parent account.` },
    { topic: 'Substance use', aAcct: `Denies current ${pick(['drug use', 'alcohol abuse', 'substance use'])}. ${pick(['Claims to be sober.', 'States use was in the past.', 'Denies any history of use.', 'Claims only occasional recreational use.'])}`, bAcct: `${pick(['Drug screen results', 'DSS observations', 'Law enforcement report', 'Medical evaluation'])} show ${pick(['positive drug screen', 'evidence of impairment', 'track marks observed', 'drug paraphernalia in home'])}.`, contra: `Lab results and ${pick(['clinical observations', 'case manager notes', 'law enforcement report'])} contradict self-report.` },
    { topic: 'Compliance with treatment plan', aAcct: `States ${pick(['full compliance', 'active participation', 'best effort', 'consistent attendance'])} with court-ordered services. Claims ${pick(['transportation issues', 'scheduling conflicts', 'provider delays'])} for any gaps.`, bAcct: `DSS records show ${pick(['minimal attendance', 'repeated no-shows', 'incomplete requirements', 'dropped out of program'])}. ${pick(['Providers confirm non-attendance.', 'Bus passes were provided but unused.', 'Alternative appointments were offered and declined.', 'No documentation of completion submitted.'])}`, contra: `Provider records and DSS documentation contradict parent claims of compliance.` },
    { topic: 'Parenting capacity', aAcct: `States ${pick(['children were always cared for', 'children were never in danger', 'is a capable parent', 'provides adequate supervision'])}. ${pick(['Blames circumstances, not parenting.', 'Claims children were happy and healthy.', 'States neighbors/family can vouch for care.'])}`, bAcct: `${pick(['School records', 'Medical records', 'Foster care reports', 'GAL observations'])} show ${pick(['chronic absenteeism', 'untreated medical needs', 'behavioral issues emerging', 'children expressed fear of returning home'])}.`, contra: `${pick(['School attendance records', 'Medical history', 'Child statements', 'GAL report'])} contradict parent account.` },
  ];

  const usedTopics = pickN(discTopics, numDisc);
  const defPid = defendant === motherName ? motherPid : fatherPid;
  const otherPid = defendant === motherName ? fatherPid : motherPid;

  for (const disc of usedTopics) {
    const doc = `${pick(DOC_TYPES)}, ${pick(DOC_TYPES)}`;
    sql.push(`INSERT INTO discrepancies (case_id, topic, person_a_id, person_a_account, person_b_id, person_b_account, contradicted_by, source_document) VALUES ('${caseId}', '${esc(disc.topic)}', ${defPid}, '${esc(disc.aAcct)}', ${Math.random() > 0.5 ? otherPid : cmPid}, '${esc(disc.bAcct)}', '${esc(disc.contra)}', '${esc(doc)}');`);
  }

  return sql.join('\n');
}

// ============================================================
// Main: Generate the full seed.sql
// ============================================================

const fs = require('fs');
const path = require('path');

// Read the hand-crafted seed data for cases 1 & 2
const handcraftedSeed = fs.readFileSync(path.join(__dirname, 'seed.sql'), 'utf-8');

// We need to account for the person_ids used by the hand-crafted data
// Case 1: 8 people (IDs 1-8), Case 2: 8 people (IDs 9-16)
personIdCounter = 16;

const output = [];
output.push('-- =============================================================');
output.push('-- DSS Legal Case Agent — Expanded Synthetic Seed Data');
output.push('-- 50 cases: 2 hand-crafted demo cases + 48 generated cases');
output.push('-- All names, dates, case numbers, and details are fictional.');
output.push('-- No real case data is represented.');
output.push('-- =============================================================');
output.push('');
output.push('-- =============================================');
output.push('-- CASES 1-2: Hand-crafted demo cases');
output.push('-- (rich data for primary demo prompts)');
output.push('-- =============================================');
output.push(handcraftedSeed);
output.push('');
output.push('-- =============================================');
output.push('-- CASES 3-50: Generated synthetic cases');
output.push('-- =============================================');

// Use seeded random for reproducibility
let seed = 42;
const origRandom = Math.random;
Math.random = function() {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const usedCaseIds = new Set(['2024-DR-42-0892', '2024-DR-15-0341']);
for (let i = 3; i <= 50; i++) {
  let caseId;
  do {
    caseId = generateCaseId(i);
  } while (usedCaseIds.has(caseId));
  usedCaseIds.add(caseId);

  output.push('');
  output.push(`-- Case ${i}: ${caseId}`);
  output.push(generateCase(caseId, i));
}

Math.random = origRandom;

// Write output
const outPath = path.join(__dirname, 'seed-expanded.sql');
fs.writeFileSync(outPath, output.join('\n'), 'utf-8');

// Summary stats
console.log(`Generated seed-expanded.sql`);
console.log(`  Total people IDs used: ${personIdCounter}`);
console.log(`  Cases: 50 (2 hand-crafted + 48 generated)`);
