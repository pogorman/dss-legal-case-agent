-- =============================================================
-- DSS Legal Case Agent — Synthetic Seed Data
-- All names, dates, case numbers, and details are fictional.
-- No real case data is represented.
-- =============================================================

-- =============================================
-- CASE 1: CPS case with medical injuries
-- =============================================
INSERT INTO cases (case_id, case_title, case_type, circuit, county, filed_date, status, plaintiff, summary)
VALUES (
    '2024-DR-42-0892',
    'DSS v. Webb & Holloway — CPS Emergency Removal',
    'Child Protective Services',
    'Seventh Judicial Circuit',
    'Spartanburg',
    '2024-06-14',
    'Active',
    'SC Department of Social Services',
    'Emergency removal of minor child Jaylen Webb (age 3) following hospital admission for multiple unexplained fractures. Parents Marcus Webb and Dena Holloway provided conflicting accounts of injuries. DSS filed for emergency protective custody. Child placed in kinship foster care with maternal grandmother. Case involves disputed timeline of events, inconsistent parental statements, and medical evidence contradicting both parents accounts.'
);

-- People for Case 1
INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES
('2024-DR-42-0892', 'Marcus Webb', 'Parent', 'Father of minor child Jaylen Webb', '1991-03-15', 'Resides at 412 Oak Hollow Rd, Spartanburg. Employed as warehouse associate. No prior DSS history.'),
('2024-DR-42-0892', 'Dena Holloway', 'Parent', 'Mother of minor child Jaylen Webb', '1993-08-22', 'Resides at same address as Marcus Webb. Employed part-time as home health aide. No prior DSS history.'),
('2024-DR-42-0892', 'Jaylen Webb', 'Child', 'Minor child, age 3', '2021-04-10', 'Subject child. Admitted to Spartanburg Medical Center on 2024-06-12 with bilateral femur fracture and spiral fracture of left humerus.'),
('2024-DR-42-0892', 'Theresa Holloway', 'Kinship Foster Parent', 'Maternal grandmother of Jaylen Webb', '1962-11-05', 'Approved kinship placement. Resides at 88 Creekside Ln, Greenville. Retired educator.'),
('2024-DR-42-0892', 'Renee Dawson', 'Case Manager', 'DSS Case Manager assigned 2024-06-13', NULL, 'Senior case manager, Spartanburg County DSS. 8 years experience. Conducted initial home assessment and all subsequent visits.'),
('2024-DR-42-0892', 'Lt. Frank Odom', 'Law Enforcement', 'Spartanburg County Sheriff investigator', NULL, 'Assigned to investigate following mandatory hospital report. Conducted interviews with both parents on 2024-06-13.'),
('2024-DR-42-0892', 'Dr. Anita Chowdhury', 'Witness', 'Attending pediatrician, Spartanburg Medical Center', NULL, 'Board-certified pediatrician. Examined Jaylen Webb on admission. Filed mandatory abuse report.'),
('2024-DR-42-0892', 'Karen Milford', 'Guardian ad Litem', 'Court-appointed GAL for Jaylen Webb', NULL, 'Appointed 2024-06-18. Attorney and volunteer GAL with SC CASA program.');

-- Timeline Events for Case 1 (12 events)
INSERT INTO timeline_events (case_id, event_date, event_time, event_type, description, source_document, parties_involved) VALUES
('2024-DR-42-0892', '2024-06-11', '10:00 PM', 'Family', 'Marcus Webb states he put Jaylen to bed at approximately 10:00 PM. Reports child was behaving normally throughout the day.', 'Dictation PDF, p. 3', 'Marcus Webb, Jaylen Webb'),
('2024-DR-42-0892', '2024-06-12', '2:00 AM', 'Medical', 'Dena Holloway reports hearing Jaylen crying loudly. Found child in crib unable to move left leg. Both parents drove child to Spartanburg Medical Center ER.', 'Dictation PDF, p. 4', 'Dena Holloway, Marcus Webb, Jaylen Webb'),
('2024-DR-42-0892', '2024-06-12', '3:15 AM', 'Medical', 'Jaylen Webb admitted to Spartanburg Medical Center ER. X-rays reveal bilateral femur fracture (right) and spiral fracture of left humerus. Injuries assessed as inconsistent with reported mechanism (fall from crib). Dr. Chowdhury notes injuries are at different stages of healing.', 'Medical Records, pp. 1-4', 'Jaylen Webb, Dr. Anita Chowdhury'),
('2024-DR-42-0892', '2024-06-12', '7:30 AM', 'Medical', 'Dr. Chowdhury files mandatory abuse/neglect report with DSS and Spartanburg County Sheriff. Medical opinion: injuries are non-accidental and occurred at different times, inconsistent with a single fall event.', 'Medical Records, p. 5; DSS Intake Report', 'Dr. Anita Chowdhury'),
('2024-DR-42-0892', '2024-06-12', '11:00 AM', 'Law Enforcement', 'Lt. Frank Odom responds to hospital. Observes child injuries. Interviews ER nursing staff. Requests DSS coordination.', 'Sheriff Report #24-06-4418, p. 1', 'Lt. Frank Odom, Jaylen Webb'),
('2024-DR-42-0892', '2024-06-13', '9:00 AM', 'DSS Action', 'Renee Dawson assigned as DSS case manager. Conducts initial assessment interview with Dena Holloway at hospital. Dena states Jaylen fell from crib and Marcus was the only adult present overnight.', 'Dictation PDF, pp. 4-6', 'Renee Dawson, Dena Holloway'),
('2024-DR-42-0892', '2024-06-13', '1:30 PM', 'Law Enforcement', 'Lt. Odom interviews Marcus Webb at Spartanburg County Sheriff office. Marcus states he was asleep on the couch and did not hear anything until Dena woke him. States he did not witness any fall.', 'Sheriff Report #24-06-4418, pp. 3-5', 'Lt. Frank Odom, Marcus Webb'),
('2024-DR-42-0892', '2024-06-13', '4:00 PM', 'Law Enforcement', 'Lt. Odom interviews Dena Holloway at Spartanburg County Sheriff office. Dena changes account — now states Marcus was in the child room earlier in the evening and she heard a loud thump around 9:30 PM but did not check immediately.', 'Sheriff Report #24-06-4418, pp. 6-8', 'Lt. Frank Odom, Dena Holloway'),
('2024-DR-42-0892', '2024-06-14', '10:00 AM', 'Court', 'DSS files petition for emergency protective custody. Family Court Judge Margaret Easley grants ex parte emergency removal order. Jaylen Webb placed in temporary DSS custody.', 'Court Filing #2024-DR-42-0892, Order 1', 'Renee Dawson, Judge Margaret Easley'),
('2024-DR-42-0892', '2024-06-18', '9:30 AM', 'Court', 'Probable cause hearing held before Judge Easley. Court finds probable cause for removal. Karen Milford appointed as Guardian ad Litem. Both parents represented by counsel. Next hearing set for 30-day review.', 'Court Filing #2024-DR-42-0892, Order 2', 'Judge Margaret Easley, Marcus Webb, Dena Holloway, Karen Milford'),
('2024-DR-42-0892', '2024-06-20', NULL, 'Placement', 'Jaylen Webb discharged from hospital and placed with maternal grandmother Theresa Holloway under kinship foster care agreement. DSS approves placement following home study.', 'Placement Agreement, DSS Form 1234', 'Jaylen Webb, Theresa Holloway, Renee Dawson'),
('2024-DR-42-0892', '2024-07-18', '2:00 PM', 'Court', 'Thirty-day review hearing. DSS presents case plan requiring parenting classes, psychological evaluations, and supervised visitation for both parents. Court approves plan. Next merits hearing scheduled for September 12, 2024.', 'Court Filing #2024-DR-42-0892, Order 3', 'Judge Margaret Easley, Marcus Webb, Dena Holloway, Renee Dawson, Karen Milford');

-- Statements for Case 1 — Marcus Webb (person_id = 1)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-42-0892', 1, '2024-06-12', 'Medical Staff', 'I put him to bed around ten. He was fine, running around all day. I fell asleep on the couch watching TV. Next thing I know, Dena is shaking me saying something is wrong with Jaylen.', 'Medical Records, Nursing Notes', 'p. 8'),
('2024-DR-42-0892', 1, '2024-06-13', 'Law Enforcement', 'I was on the couch all night. I did not go into Jaylen room after I put him down. I don''t know how he got hurt. Maybe he climbed out of the crib and fell. He''s been trying to climb out lately.', 'Sheriff Report #24-06-4418', 'p. 4'),
('2024-DR-42-0892', 1, '2024-06-13', 'Law Enforcement', 'Dena and I have been arguing a lot lately but I would never hurt my son. I don''t know why she is saying I was in the room. I was not in his room after 10 PM.', 'Sheriff Report #24-06-4418', 'p. 5'),
('2024-DR-42-0892', 1, '2024-06-14', 'Case Manager', 'I love my son. I want to cooperate with DSS. I will do whatever the court says. I did not hurt Jaylen and I don''t know what happened to him.', 'Dictation PDF', 'p. 12'),
('2024-DR-42-0892', 1, '2024-07-18', 'Court', 'I have enrolled in parenting classes at Spartanburg Family Services. I want to get my son back. I am willing to do everything in the case plan.', 'Court Transcript, 30-Day Review', 'p. 22');

-- Statements for Case 1 — Dena Holloway (person_id = 2)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-42-0892', 2, '2024-06-12', 'Medical Staff', 'I heard him crying around 2 AM. I went in and he couldn''t move his leg. I think he fell out of his crib. Marcus put him to bed, I was in the bedroom.', 'Medical Records, Nursing Notes', 'p. 9'),
('2024-DR-42-0892', 2, '2024-06-13', 'Case Manager', 'Marcus was the only one with Jaylen after bedtime. I was in our bedroom with the door closed. I didn''t hear anything until 2 AM when Jaylen started screaming.', 'Dictation PDF', 'p. 5'),
('2024-DR-42-0892', 2, '2024-06-13', 'Law Enforcement', 'Actually, I need to correct something. Around 9:30 PM I heard a loud thump from Jaylen room. I assumed Marcus was in there. I called out and Marcus said everything was fine. I did not check on Jaylen at that time.', 'Sheriff Report #24-06-4418', 'p. 7'),
('2024-DR-42-0892', 2, '2024-06-13', 'Law Enforcement', 'Marcus has a temper. He gets frustrated when Jaylen won''t stop crying. I have seen him grab Jaylen roughly by the arm before, maybe two or three times. I should have said something sooner.', 'Sheriff Report #24-06-4418', 'p. 8'),
('2024-DR-42-0892', 2, '2024-06-14', 'Case Manager', 'I want Jaylen to be safe. If my mama can take him, that would be best right now. I don''t feel safe with Marcus around Jaylen until we figure out what happened.', 'Dictation PDF', 'p. 14');

-- Statements for Case 1 — Renee Dawson (person_id = 5)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-42-0892', 5, '2024-06-13', 'Case Manager', 'During my initial interview with Ms. Holloway at the hospital, she appeared nervous and avoided eye contact when discussing the evening of June 11. Her account changed significantly between the hospital interview and the sheriff interview later that day.', 'Dictation PDF', 'p. 6'),
('2024-DR-42-0892', 5, '2024-06-14', 'Court', 'Based on my assessment, the child is at imminent risk of harm if returned to either parent at this time. The medical evidence indicates non-accidental trauma and both parents have provided inconsistent accounts. I recommend emergency removal and kinship placement with the maternal grandmother.', 'Dictation PDF', 'p. 15'),
('2024-DR-42-0892', 5, '2024-06-20', 'Case Manager', 'Home study of Theresa Holloway residence completed. Home is clean, safe, and age-appropriate for a three-year-old. Ms. Holloway is cooperative and understands the placement requirements.', 'Home Study Report', 'p. 2');

-- Statements for Case 1 — Dr. Chowdhury (person_id = 7)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-42-0892', 7, '2024-06-12', 'Medical Staff', 'The fracture pattern is inconsistent with a fall from a standard crib height. The spiral fracture of the left humerus indicates torsional force. Additionally, radiographic findings suggest the femur fracture is approximately 24-48 hours older than the humerus fracture, indicating two separate injury events.', 'Medical Records', 'p. 5'),
('2024-DR-42-0892', 7, '2024-06-18', 'Court', 'In my medical opinion, these injuries are non-accidental. A three-year-old falling from a crib would not sustain bilateral long bone fractures of this nature. The different healing stages confirm at least two separate trauma events occurring days apart.', 'Court Transcript, Probable Cause Hearing', 'p. 14');

-- Discrepancies for Case 1 (6 discrepancies)
INSERT INTO discrepancies (case_id, topic, person_a_id, person_a_account, person_b_id, person_b_account, contradicted_by, source_document) VALUES
('2024-DR-42-0892', 'Cause of child injuries', 1, 'States Jaylen may have fallen from crib while climbing. Claims the child had been trying to climb out of the crib recently.', 2, 'Initially agreed child fell from crib, but later stated she heard a thump at 9:30 PM from Jaylen room while Marcus was present.', 'Medical records indicate injuries are non-accidental and occurred at two separate times, inconsistent with a single fall event.', 'Medical Records pp. 1-5; Sheriff Report #24-06-4418'),
('2024-DR-42-0892', 'Marcus Webb presence in child room', 1, 'States he put Jaylen to bed at 10 PM and did not re-enter the room. Was on the couch all night.', 2, 'States she heard a thump from Jaylen room at 9:30 PM, called out, and Marcus responded that everything was fine — placing Marcus in or near the room at 9:30 PM.', 'Dena''s revised statement to Lt. Odom contradicts Marcus claim he was not in the room after 10 PM. The thump occurred before the stated bedtime.', 'Sheriff Report #24-06-4418, pp. 4-8'),
('2024-DR-42-0892', 'Timing of injury discovery', 1, 'States Dena woke him on the couch when she found Jaylen crying at 2 AM. Implies he was unaware of any problem before that.', 2, 'States she heard a loud thump at 9:30 PM but did not check because Marcus said everything was fine. Did not discover injury until 2 AM.', 'If the thump at 9:30 PM was the injury event, there was a 4.5-hour delay before seeking medical attention. Medical staff note this delay is concerning.', 'Medical Records, Nursing Notes p. 9; Sheriff Report #24-06-4418'),
('2024-DR-42-0892', 'History of rough handling', 1, 'Denies ever handling Jaylen roughly. States he has never harmed his child and does not know how the injuries occurred.', 2, 'States Marcus has a temper and she has seen him grab Jaylen roughly by the arm two or three times when frustrated by crying.', 'Dena''s statement to law enforcement. No prior DSS reports on file, but Dena''s account suggests a pattern not previously reported.', 'Sheriff Report #24-06-4418, p. 8'),
('2024-DR-42-0892', 'Single vs. multiple injury events', 1, 'Account implies a single incident — child fell from crib overnight.', 2, 'Account implies at least one event at 9:30 PM (thump) and a separate discovery at 2 AM.', 'Dr. Chowdhury confirms fractures are at different healing stages, indicating injuries occurred days apart — contradicting both parents'' accounts of a single night.', 'Medical Records, p. 5; Court Transcript p. 14'),
('2024-DR-42-0892', 'Dena Holloway initial vs. revised account', 2, 'Hospital statement (June 12): Heard crying at 2 AM, found child injured, believes he fell from crib. No mention of 9:30 PM thump or Marcus being in the room.', 2, 'Sheriff interview (June 13 PM): Reveals she heard a thump at 9:30 PM, Marcus was in or near the room, and she has witnessed Marcus grab Jaylen roughly before.', 'Dena''s own statements are internally inconsistent. Initial account omitted critical details that she later disclosed under law enforcement questioning.', 'Medical Records p. 9; Sheriff Report #24-06-4418 pp. 6-8');


-- =============================================
-- CASE 2: Termination of Parental Rights (TPR)
-- =============================================
INSERT INTO cases (case_id, case_title, case_type, circuit, county, filed_date, status, plaintiff, summary)
VALUES (
    '2024-DR-15-0341',
    'DSS v. Price — Termination of Parental Rights',
    'Termination of Parental Rights',
    'Fifth Judicial Circuit',
    'Richland',
    '2024-02-08',
    'Active',
    'SC Department of Social Services',
    'Petition for termination of parental rights of Crystal Price regarding minor children Amari Price (age 7) and Destiny Price (age 5). Children were removed in August 2023 following substantiated neglect findings. Ms. Price failed to complete court-ordered treatment plan including substance abuse counseling, parenting classes, and stable housing requirements over a 12-month reunification period. Father Brandon Price''s rights were voluntarily relinquished in November 2023. Probable cause hearing completed; merits hearing scheduled. Children currently in licensed foster care with pre-adoptive family.'
);

-- People for Case 2
INSERT INTO people (case_id, full_name, role, relationship, dob, notes) VALUES
('2024-DR-15-0341', 'Crystal Price', 'Parent', 'Mother of minor children Amari and Destiny Price', '1989-12-03', 'Resides at various addresses in Richland County. History of substance abuse (opioids). Two prior DSS investigations in 2021 and 2022, both unsubstantiated.'),
('2024-DR-15-0341', 'Brandon Price', 'Parent', 'Father of minor children Amari and Destiny Price', '1987-06-19', 'Incarcerated at Kirkland Correctional Institution since March 2023. Voluntarily relinquished parental rights November 2023.'),
('2024-DR-15-0341', 'Amari Price', 'Child', 'Minor child, age 7', '2017-09-28', 'Currently placed with licensed foster family, the Pattersons. Enrolled in second grade at Longleaf Elementary.'),
('2024-DR-15-0341', 'Destiny Price', 'Child', 'Minor child, age 5', '2019-05-14', 'Currently placed with licensed foster family, the Pattersons. Enrolled in pre-K at Longleaf Elementary.'),
('2024-DR-15-0341', 'Monica Vance', 'Case Manager', 'DSS Case Manager assigned August 2023', NULL, 'Case manager, Richland County DSS. Managed case from initial removal through TPR filing.'),
('2024-DR-15-0341', 'Dr. Raymond Ellis', 'Witness', 'Licensed clinical social worker, substance abuse evaluator', NULL, 'Conducted substance abuse evaluation of Crystal Price in September 2023. Recommended intensive outpatient treatment.'),
('2024-DR-15-0341', 'Sandra Patterson', 'Foster Parent', 'Licensed foster parent, pre-adoptive placement', NULL, 'Licensed foster parent since 2019. Children placed August 2023. Family has expressed intent to adopt if TPR is granted.'),
('2024-DR-15-0341', 'Thomas Reed', 'Guardian ad Litem', 'Court-appointed GAL for Amari and Destiny Price', NULL, 'Appointed September 2023. Recommends TPR and adoption by Patterson family.');

-- Timeline Events for Case 2 (10 events)
INSERT INTO timeline_events (case_id, event_date, event_time, event_type, description, source_document, parties_involved) VALUES
('2024-DR-15-0341', '2023-08-05', '3:00 PM', 'DSS Action', 'DSS receives referral from Longleaf Elementary School regarding Amari Price. Teacher reports child has come to school hungry on multiple occasions, wearing dirty clothes, and disclosed that mother sleeps all day and there is no food at home.', 'DSS Intake Report #23-08-1102', 'Amari Price, Monica Vance'),
('2024-DR-15-0341', '2023-08-08', '10:00 AM', 'DSS Action', 'Monica Vance conducts unannounced home visit at 1547 Gervais St, Apt 4B, Columbia. Finds apartment in unsanitary condition — spoiled food, no running water (utility shutoff), drug paraphernalia visible on kitchen counter. Crystal Price appears impaired. Both children present and unsupervised.', 'Home Visit Report', 'Monica Vance, Crystal Price, Amari Price, Destiny Price'),
('2024-DR-15-0341', '2023-08-08', '4:00 PM', 'DSS Action', 'DSS obtains emergency removal order. Amari and Destiny Price placed in emergency foster care. Crystal Price informed of removal and her rights.', 'Court Filing #2023-DR-15-0341, Emergency Order', 'Monica Vance, Crystal Price, Amari Price, Destiny Price'),
('2024-DR-15-0341', '2023-08-15', '9:00 AM', 'Court', 'Probable cause hearing for removal. Court finds probable cause of neglect. Crystal Price present with appointed counsel. Court orders treatment plan: substance abuse evaluation, parenting classes, stable housing, and employment. Reunification review in 90 days.', 'Court Filing, Order 1', 'Crystal Price, Monica Vance, Judge Harold Wynn'),
('2024-DR-15-0341', '2023-09-10', NULL, 'Medical', 'Dr. Raymond Ellis conducts substance abuse evaluation of Crystal Price. Diagnosis: Opioid Use Disorder, moderate severity. Recommends intensive outpatient program (IOP) with random drug testing.', 'Substance Abuse Evaluation Report', 'Dr. Raymond Ellis, Crystal Price'),
('2024-DR-15-0341', '2023-09-25', NULL, 'Placement', 'Amari and Destiny Price placed with Sandra and Michael Patterson, licensed foster family in Richland County. Children enrolled at Longleaf Elementary. Foster family expresses interest in adoption if reunification fails.', 'Placement Agreement', 'Amari Price, Destiny Price, Sandra Patterson, Monica Vance'),
('2024-DR-15-0341', '2023-11-14', NULL, 'Court', 'Ninety-day review hearing. Crystal Price has attended 3 of 12 required IOP sessions. Has not enrolled in parenting classes. No stable housing. Two positive drug screens (fentanyl) in October. Court continues treatment plan, warns that failure to comply may result in TPR.', 'Court Filing, Order 2', 'Crystal Price, Monica Vance, Judge Harold Wynn'),
('2024-DR-15-0341', '2023-11-20', NULL, 'Court', 'Brandon Price voluntarily relinquishes parental rights via written consent filed with the court. Mr. Price states from Kirkland Correctional that he wants what is best for the children and cannot parent from incarceration.', 'Voluntary Relinquishment Filing', 'Brandon Price, Judge Harold Wynn'),
('2024-DR-15-0341', '2024-02-08', '10:00 AM', 'Court', 'DSS files petition for Termination of Parental Rights against Crystal Price. Grounds: (1) child neglect, (2) failure to remedy conditions causing removal for more than six months despite court-ordered treatment plan, (3) substance abuse rendering parent unable to provide minimally adequate care.', 'TPR Petition #2024-DR-15-0341', 'Monica Vance, Crystal Price, Thomas Reed'),
('2024-DR-15-0341', '2024-04-22', '9:30 AM', 'Court', 'TPR probable cause hearing. Court finds probable cause to proceed to merits hearing. Crystal Price has now completed 5 of 12 IOP sessions, enrolled in parenting classes (attended 2 of 8), and obtained temporary housing. Court notes progress but finds it insufficient given 8-month timeframe. Merits hearing scheduled for July 15, 2024.', 'Court Filing, Order 3', 'Crystal Price, Monica Vance, Judge Harold Wynn, Thomas Reed');

-- Statements for Case 2 — Crystal Price (person_id = 9, first person in case 2)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-15-0341', 9, '2023-08-08', 'Case Manager', 'I''m going through a hard time. Brandon is locked up and I lost my job. The kids are fine, I take care of them. I just need some help with the bills.', 'Home Visit Report', 'p. 3'),
('2024-DR-15-0341', 9, '2023-08-15', 'Court', 'I love my children. I know I need to get help. I will do everything the court asks. Please don''t take my babies.', 'Court Transcript, Probable Cause Hearing', 'p. 18'),
('2024-DR-15-0341', 9, '2023-11-14', 'Court', 'I have been trying to get to the IOP sessions but I don''t have reliable transportation. I missed some appointments. I am looking for housing but it is hard without income. I am clean now.', 'Court Transcript, 90-Day Review', 'p. 12'),
('2024-DR-15-0341', 9, '2024-02-08', 'Case Manager', 'I know I messed up but I am getting better. I started going to NA meetings. I found a room to rent. I just need more time. Six months is not enough when you have nothing.', 'Dictation PDF', 'p. 8'),
('2024-DR-15-0341', 9, '2024-04-22', 'Court', 'I have been going to my IOP sessions and parenting classes. I have a place to stay now. I am working part-time at a gas station. I am trying. I want my kids back.', 'Court Transcript, TPR Probable Cause', 'p. 20');

-- Statements for Case 2 — Monica Vance (person_id = 13)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-15-0341', 13, '2023-08-08', 'Case Manager', 'Upon entering the apartment, I observed drug paraphernalia on the kitchen counter including a burnt spoon and syringe. The refrigerator contained only condiments and a gallon of spoiled milk. Both children were in the living room watching television. Amari told me he was hungry.', 'Home Visit Report', 'p. 2'),
('2024-DR-15-0341', 13, '2023-11-14', 'Court', 'Ms. Price has attended only 3 of 12 required IOP sessions. She has not enrolled in parenting classes as ordered. She has had two positive drug screens for fentanyl in October. She does not have stable housing — she reports staying with various friends. I have attempted six home visits and reached her twice.', 'Court Transcript, 90-Day Review', 'p. 8'),
('2024-DR-15-0341', 13, '2024-02-08', 'Court', 'Over the six months since removal, Ms. Price has made minimal progress on her treatment plan. She has completed 3 of 12 IOP sessions, has not completed parenting classes, has no stable housing, and has had multiple positive drug screens. DSS has provided bus passes, referrals, and assistance with housing applications. Despite these supports, compliance has been insufficient.', 'TPR Petition, Affidavit', 'pp. 4-5'),
('2024-DR-15-0341', 13, '2024-04-22', 'Court', 'Since the TPR petition was filed, Ms. Price has increased engagement. She has now completed 5 of 12 IOP sessions, attended 2 of 8 parenting classes, and obtained a room in a shared house. However, the shared housing would not be appropriate for two children. Her most recent drug screen on April 10 was negative. While there is progress, it remains well below what was ordered eight months ago.', 'Court Transcript, TPR Probable Cause', 'p. 10');

-- Statements for Case 2 — Dr. Ellis (person_id = 14)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-15-0341', 14, '2023-09-10', 'Case Manager', 'Ms. Price meets diagnostic criteria for Opioid Use Disorder, moderate severity. She reports daily opioid use beginning in 2021 following a back injury. She has not previously sought treatment. I recommend intensive outpatient treatment, minimum 12 sessions, combined with random drug screening and NA or similar peer support.', 'Substance Abuse Evaluation Report', 'pp. 3-4');

-- Statements for Case 2 — Thomas Reed, GAL (person_id = 16)
INSERT INTO statements (case_id, person_id, statement_date, made_to, statement_text, source_document, page_reference) VALUES
('2024-DR-15-0341', 16, '2024-02-08', 'Court', 'I have visited the children three times in the Patterson home. Both children are thriving — Amari is performing at grade level and Destiny has adjusted well to pre-K. The Pattersons provide a stable, loving home and wish to adopt. In my assessment, termination of parental rights and adoption is in the best interest of both children.', 'GAL Report', 'pp. 1-2'),
('2024-DR-15-0341', 16, '2024-04-22', 'Court', 'While I acknowledge Ms. Price''s recent efforts, the children have now been in foster care for eight months. They are bonded with the Patterson family and are stable for the first time in their lives. Further delays in permanency are not in the children''s best interest. I continue to recommend TPR.', 'GAL Report, Updated', 'p. 2');

-- Discrepancies for Case 2 (4 discrepancies)
INSERT INTO discrepancies (case_id, topic, person_a_id, person_a_account, person_b_id, person_b_account, contradicted_by, source_document) VALUES
('2024-DR-15-0341', 'Condition of the home at removal', 9, 'States the kids are fine and she just needs help with bills. Implies the home conditions are acceptable and the primary issue is financial.', 13, 'Documents drug paraphernalia visible on kitchen counter, no food in refrigerator, no running water due to utility shutoff. Children were unsupervised and Amari reported being hungry.', 'Home visit observations and photographs. Utility company confirmed shutoff on July 28, 2023 for nonpayment.', 'Home Visit Report, pp. 2-3'),
('2024-DR-15-0341', 'Drug use and sobriety', 9, 'States at 90-day review that she is clean now. At TPR probable cause states she is getting better and attending NA meetings.', 13, 'Documents two positive drug screens for fentanyl in October 2023, three months after removal. Most recent screen (April 2024) was negative, but compliance with testing has been inconsistent.', 'Lab results from October 8 and October 22, 2023 both positive for fentanyl. Missed scheduled screens on December 5, January 15, and March 3.', 'Drug Screen Reports; Court Transcript pp. 8, 12'),
('2024-DR-15-0341', 'Compliance with treatment plan', 9, 'States she has been trying but lacks transportation and support. Claims she is actively working on all requirements.', 13, 'Documents that DSS provided bus passes, referral assistance, and help with housing applications. Despite supports, Ms. Price completed only 5 of 12 IOP sessions and 2 of 8 parenting classes in 8 months.', 'DSS records show bus passes issued monthly, three housing referrals provided, and IOP transportation assistance offered but declined.', 'Dictation PDF p. 8; Court Transcripts'),
('2024-DR-15-0341', 'Housing stability', 9, 'Claims at TPR probable cause that she has a place to stay and is working part-time. Implies progress toward meeting housing requirement.', 13, 'Reports Ms. Price is renting a single room in a shared house that would not be appropriate for two children. Previous addresses include at least four different locations since removal.', 'Housing inspection notes that room is approximately 10x10 with shared bathroom. Landlord confirms month-to-month arrangement with no lease.', 'Housing Inspection Report; Court Transcript p. 10');
