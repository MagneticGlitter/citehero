# Iliad Book 1 Investigator/RAG Drill-Down Evaluation

This is a markdown-only evaluation artifact. No deterministic unit-test files were created. Each case was run against `iliad_book1` with `python main.py ask --reading-id iliad_book1 --top-k 10`, then delegated to a separate subagent for lightweight checks and qualitative scoring.

## Rubric


| Metric              | Meaning                                                          |
| ------------------- | ---------------------------------------------------------------- |
| retrieval_relevance | Did the retrieved pages/chunks target the expected evidence?     |
| citation_accuracy   | Do citations directly support the claims?                        |
| speaker_attribution | Are speakers/actions attributed to the right figures?            |
| causal_chain        | Does the response preserve event sequence and causal links?      |
| no_hallucination    | Does it avoid unsupported outside or invented claims?            |
| answer_quality      | Is the final answer direct, clear, useful, and correctly scoped? |


## Cross-case summary

- The dominant failure is **generation/answer formatting**: many outputs return `Best evidence` snippets instead of a synthesized answer.
- Retrieval often finds at least one relevant page, but **misses crucial adjacent or transitional pages**, especially for multi-hop/causal and essay questions.
- Reranking overweights lexical matches such as `dishonoured` or named entities and underweights **who was dishonoured** and **what action follows**.
- OCR is generally usable; minor OCR noise exists (`I0`, `takc`, `Briscis`, line-number artifacts) but is not the primary failure.
- Improvements should prioritize: direct-answer prompt guardrails, page-window expansion, page/entity coverage constraints for broad questions, and citation validation against required concepts.

## Q1. Who is Chryses, and what does he ask the Achaians to do?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: pp. 1–2
- Good answer should mention: Chryses is a priest of Apollo; he comes with ransom to recover his daughter; Agamemnon rejects him.
- Failure signs: Confuses Chryses with Chryseis; says he is a warrior; misses Apollo.

### Investigator response

```md
Question: Who is Chryses, and what does he ask the Achaians to do?
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 11] Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons...
Evidence:
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 11 | p0011_c01] Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people.
```

### Subagent evaluation

**Question:** Who is Chryses, and what does he ask the Achaians to do?  
**Expected pages:** pp. 1–2

## Lightweight checks

- **Expected-page coverage:** Partial. The result cites **p. 1**, but misses **p. 2**, where Agamemnon's explicit rejection and threats appear. It also cites **p. 3** and **p. 11**; p. 11 is a later recap and relevant, but p. 3 is only indirectly related.
- **Missing citations:** The response provides cited evidence snippets, but it does **not provide a synthesized answer**. The key rejection evidence should cite p. 2 or the p. 11 recap.
- **Forbidden failure signs:** No clear forbidden sign appears: it does not call Chryses a warrior, does not confuse him with Chryseis, and does include Apollo. However, the absence of a direct answer makes this a functional failure for a simple factual question.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                            |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| retrieval_relevance | 3/5   | p. 1 is highly relevant and p. 11 is a relevant recap, but p. 2 is missing and p. 3 is low-value for this question.                                                                                                                              |
| citation_accuracy   | 3/5   | The cited snippets accurately support pieces of the answer, especially Chryses as Apollo's priest and his request for ransom. But the rejection component is under-supported without p. 2, and p. 3 is not a good citation for the asked fact.   |
| speaker_attribution | n/a   | The answer does not really discuss speakers beyond quoted source context. No misattribution, but not enough synthesized content to evaluate.                                                                                                     |
| causal_chain        | 2/5   | Evidence hints at the chain: Chryses asks, Agamemnon dishonors/refuses him, Apollo sends plague. But the response itself does not explain the chain.                                                                                             |
| no_hallucination    | 5/5   | No unsupported claim is introduced; the problem is omission/synthesis, not hallucination.                                                                                                                                                        |
| answer_quality      | 1/5   | It gives “Best evidence” rather than answering. A good answer should say: Chryses is a priest of Apollo who comes with ransom to recover his daughter, asks the Achaians/Atreids to return her and accept the ransom, and Agamemnon rejects him. |


## Diagnosis

- **Primary issue: generation / prompt.** The system retrieved enough evidence to answer the core question, especially from p. 1, but the generated response failed to synthesize an actual answer and only listed evidence.
- **Secondary issue: retrieval or reranking.** The expected p. 2 passage was not retrieved, while p. 3 was included despite being less directly relevant. p. 11 is relevant as a recap, but for this question p. 2 would have been the better citation for Agamemnon's rejection.
- **OCR:** Not a meaningful issue here. The relevant OCR text on pp. 1–2 is readable and accurate enough.

## Overall judgment

The RAG result is **partially grounded but not satisfactory**. It surfaces important evidence that Chryses is Apollo's priest and comes to ransom his daughter, but it does not directly answer the question and misses the strongest expected citation for Agamemnon's rejection on p. 2.

## Q2. Who is Kalchas, and why is he afraid to speak?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: p. 3
- Good answer should mention: Kalchas is a seer/bird-interpreter; he knows the cause of Apollo’s anger; he fears Agamemnon’s reaction; Achilles promises protection.
- Failure signs: Says Kalchas was dishonoured by Agamemnon; confuses him with Chryses.

### Investigator response

```md
Question: Who is Kalchas, and why is he afraid to speak?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

## Lightweight checks

- **Expected page:** p. 3 — **pass**. Retrieved evidence is from p. 3, the correct page.
- **Missing citations:** **partial fail**. The response cites p. 3 and includes a relevant evidence chunk, but it gives no direct synthesized answer beyond “Best evidence.”
- **Forbidden failure signs:** **pass**. It does **not** say Kalchas was dishonoured by Agamemnon and does **not** confuse him with Chryses.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                                 |
| ------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 4/5   | The cited chunk is highly relevant to Kalchas’s fear and Achilles’ protection, but it starts at Achilles’ promise and omits the immediately preceding identification of Kalchas as “Thestor’s son” and “best of the bird interpreters.”               |
| citation_accuracy   | 4/5   | The p. 3 citation supports the fear/protection portion accurately. It is incomplete for identifying who Kalchas is because the quoted evidence begins after the key identifying lines.                                                                |
| speaker_attribution | 3/5   | The evidence itself makes clear Achilles is speaking in the quoted promise, and then Kalchas speaks, but the generated response does not explicitly attribute the information in prose.                                                               |
| causal_chain        | 2/5   | The evidence includes enough to infer the chain: Kalchas fears angering Agamemnon, Achilles promises protection, Kalchas reveals Apollo’s anger is due to Agamemnon dishonouring Chryses. However, the response does not actually explain that chain. |
| no_hallucination    | 5/5   | No unsupported claims are introduced. The main issue is omission, not hallucination.                                                                                                                                                                  |
| answer_quality      | 1/5   | As an answer to the user’s question, it is inadequate: it returns evidence only and does not state clearly that Kalchas is a seer/bird-interpreter who fears Agamemnon’s retaliation for revealing the cause of Apollo’s plague.                      |


## Diagnosis

Primary issue: **generation / prompt**.

Retrieval succeeded enough to find the correct page and relevant passage. The evidence chunk is slightly narrow, missing the earlier lines that identify Kalchas as the best bird-interpreter, so there may be a minor **retrieval chunking** issue. But the larger failure is that the system did not synthesize the answer from the evidence; it only presented a quote. There is no sign of OCR failure, and no reranking problem is apparent because the top evidence is on the expected page and relevant.

## Overall judgment

The result is factually safe and retrieves the right source page, but it fails the simple factual lookup task because it does not directly answer both parts of the question. A good response should have said: Kalchas is Thestor’s son, a seer/bird-interpreter who knows Apollo’s will; he is afraid to speak because revealing that Apollo is angry over Agamemnon’s treatment of Chryses will anger Agamemnon, so Achilles promises to protect him.

## Q3. Why does Apollo send a plague against the Achaians?

**Test set:** A — Simple factual lookup

### Expected

- Expected evidence: pp. 1–3
- Good answer should mention: Agamemnon dishonoured Chryses and refused to return Chryseis; Apollo punishes the army.
- Failure signs: Says Achilles caused the plague; cites only later Achilles/Agamemnon quarrel pages.

### Investigator response

```md
Question: Why does Apollo send a plague against the Achaians?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
```

### Subagent evaluation

**Question:** Why does Apollo send a plague against the Achaians?  
**Expected pages:** pp. 1–3  
**Expected answer:** Agamemnon dishonoured Chryses, Apollo's priest, by refusing the ransom and refusing to return Chryseis; Apollo punishes the Achaian army in response.

## Lightweight checks

- **Expected-page coverage:** Pass/partial. Retrieved/cited **p. 1** and **p. 3**, both within the expected range. It did not cite p. 2, which contains Chryses' prayer and Apollo beginning the plague, but p. 1 and p. 3 are sufficient for the causal answer.
- **Missing citations:** No formal missing-citation problem: citations are present for both evidence bullets. However, the generated response itself is mostly evidence excerpts, not a synthesized answer.
- **Forbidden failure signs:** Pass. It does **not** say Achilles caused the plague, and it does **not** cite only later Achilles/Agamemnon quarrel pages.

## Source check

- **p. 1** explicitly states Apollo sent the pestilence because Atreus' son dishonoured Chryses, priest of Apollo, when Chryses came to ransom his daughter.
- **p. 2** adds the immediate sequence: Agamemnon harshly drives Chryses away; Chryses prays to Apollo to make the Danaans pay; Apollo hears and shoots plague-arrows into the camp.
- **p. 3** has Kalchas' explanation: Apollo blames them for Agamemnon's dishonouring of his priest and refusal to return the daughter or accept ransom.

## Rubric


| Criterion           | Score | Notes                                                                                                                                                                         |
| ------------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 4     | Retrieves highly relevant p. 1 and p. 3. Missing p. 2 loses some causal-chain detail, but not fatal.                                                                          |
| citation_accuracy   | 4     | Page citations are accurate and support the answer. The p. 3 excerpt shown in the response starts too early and is truncated around the key explanation.                      |
| speaker_attribution | 3     | The evidence implies Kalchas explains the cause and p. 1 gives narrator summary, but the response does not clearly synthesize or attribute speakers.                          |
| causal_chain        | 3     | The key cause is present in cited evidence, especially p. 1, but the response does not plainly state the chain: Agamemnon dishonours Chryses → Chryses/Apollo anger → plague. |
| no_hallucination    | 5     | No unsupported claims or incorrect causal claims detected.                                                                                                                    |
| answer_quality      | 2     | The response is evidence dump style: it gives “Best evidence” rather than a direct answer. A reader can infer the answer, but it is not clearly stated.                       |


## Diagnosis

Primary issue: **generation/prompt**. Retrieval found relevant pages, and OCR is good enough despite minor line-number/OCR artifacts. The system failed to convert the retrieved evidence into a concise answer. There may also be a small **reranking/snippet-selection** issue because the p. 3 snippet begins at Achilles' reassurance to Kalchas and truncates before or around Kalchas' actual explanation, while p. 2 was not included. Overall, this is not an OCR failure and not a severe retrieval failure.

## Overall judgment

The result is factually grounded and cites relevant expected pages, but it underperforms as an answer because it does not explicitly say: **Apollo sends the plague because Agamemnon dishonoured Chryses, Apollo's priest, by refusing the ransom and refusing to return Chryseis; Apollo punishes the Achaians for that insult.**

## Q4. Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 11–12
- Good answer should mention: Achilles asks Thetis; he wants Zeus to help the Trojans and push the Achaians back so Agamemnon realizes his mistake.
- Failure signs: Says Thetis asks Achilles; says Achilles directly prays to Zeus; misses the purpose of punishing the Achaians.

### Investigator response

```md
Question: Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?
Response: Best evidence:
- [p. 14] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the mornin...
- [p. 15] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father,...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 14 | p0014_c01] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos.
- [p. 15 | p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** Who asks Thetis to appeal to Zeus, and what does he want Zeus to do?  
**Expected answer:** Achilles asks Thetis; he wants Zeus to help the Trojans drive the Achaians back to their ships so Agamemnon recognizes his dishonor/mistake.

## Lightweight checks

- **Expected pages:** Expected pp. 11–12. The response cites **p. 14, p. 15, and p. 3** only, so it misses the key request scene on pp. 11–12.
- **Missing citations:** Yes. It does not cite p. 11 where Achilles directly tells Thetis to go to Olympos and supplicate Zeus, nor p. 12 where he specifies helping the Trojans and pinning the Achaians back.
- **Forbidden failure signs:**
  - Does **not** explicitly say Thetis asks Achilles.
  - Does **not** explicitly say Achilles directly prays to Zeus.
  - Partly misses the purpose: p. 14 evidence includes Thetis asking Zeus to strengthen the Trojans, but the response does not clearly state the causal aim of punishing the Achaians / forcing Agamemnon to recognize his mistake.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                 |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | p. 14 is related because it shows Thetis carrying out Achilles’ request, but pp. 11–12—the direct answer—are absent. p. 15 is only follow-up, and p. 3 is irrelevant. |
| citation_accuracy   | 2/5   | The cited snippets are real and accurately quoted, but they do not support the full answer well and omit the strongest citations.                                     |
| speaker_attribution | 2/5   | p. 14 says “entreaties of her son,” which implies Achilles, but the response never directly answers that Achilles asks Thetis.                                        |
| causal_chain        | 2/5   | It partially surfaces the Trojan-help request via p. 14, but does not clearly connect it to pushing the Achaians back so Agamemnon recognizes his wrong.              |
| no_hallucination    | 4/5   | No major invented claim; the issue is omission and weak synthesis rather than hallucination.                                                                          |
| answer_quality      | 1/5   | The response is essentially an evidence list, not a direct answer to the question. It misses the expected direct citations and leaves the user to infer the answer.   |


## Diagnosis

Primary issue: **retrieval/reranking**, with a secondary **generation/prompt** issue.

- Retrieval/reranking failed to surface the expected pp. 11–12, where Achilles’ request is explicit: “protect your own son, going to Olympos and supplicating Zeus” and “help the Trojans, and pin the Achaians back…”
- Generation also failed because it did not synthesize a direct answer from the available evidence. Even with p. 14, it could have answered that Thetis acted on her son Achilles’ entreaties and asked Zeus to strengthen the Trojans.
- OCR does **not** appear to be the cause; the relevant pp. 11–12 text is readable and adequate.
- Prompting may contribute if the system is biased toward returning “Best evidence” rather than answering first with a concise claim.

## Overall judgment

The result is **partially relevant but inadequate**. It avoids the most serious false attribution errors, but it fails the core task because it does not directly answer who asked Thetis or clearly explain Achilles’ intended outcome, and it misses the expected source pages.

## Q5. What does Thetis ask Zeus to do for Achilles?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: pp. 14–15
- Good answer should mention: Thetis asks Zeus to honour Achilles by giving strength to the Trojans until the Achaians restore Achilles’ honour.
- Failure signs: Says Thetis asks Zeus to return Briseis; says Zeus helps Achilles fight directly.

### Investigator response

```md
Question: What does Thetis ask Zeus to do for Achilles?
Response: Best evidence:
- [p. 14] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the mornin...
- [p. 15] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father,...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 14 | p0014_c01] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos.
- [p. 15 | p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

**Question:** What does Thetis ask Zeus to do for Achilles?  
**Expected evidence:** pp. 14–15, especially p. 14 lines 503–510: Thetis asks Zeus to honor Achilles by strengthening/helping the Trojans until the Achaians restore/increase Achilles’ honor.

## Lightweight checks

- **Expected pages present:** Partial pass. The result retrieves/cites **p. 14** and **p. 15**, which are the correct pages.
- **Key evidence actually cited:** Mostly fail. The cited p. 14 chunk stops before the crucial request: “Now give honour…” / “put strength into the Trojans…” / “until the Achaians give my son his rights…” The p. 15 citation supports Zeus agreeing but not Thetis’s actual request.
- **Irrelevant citation:** Yes. **p. 3** is unrelated to Thetis’s appeal to Zeus.
- **Missing answer:** Yes. The response gives “Best evidence” and “Evidence” snippets but does not directly answer the question.
- **Forbidden failure signs:** Not present. It does **not** say Thetis asks Zeus to return Briseis, and does **not** say Zeus helps Achilles fight directly.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                    |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 3/5   | Correct pages p. 14–15 are retrieved, but the p. 14 chunk misses the decisive lines, and p. 3 is irrelevant.                                                                             |
| citation_accuracy   | 2/5   | Page labels are accurate, but citations do not include the main textual support for the answer.                                                                                          |
| speaker_attribution | n/a   | No substantive answer is generated, so attribution cannot really be assessed. The evidence context does identify Thetis, but the response does not state her request.                    |
| causal_chain        | n/a   | No answer explaining the chain is provided. Expected chain: Agamemnon dishonors Achilles → Thetis asks Zeus to honor him → Trojans gain strength until Achaians restore Achilles’ honor. |
| no_hallucination    | 5/5   | No incorrect claim is made; the problem is omission, not hallucination.                                                                                                                  |
| answer_quality      | 1/5   | The response fails to answer the user’s question and only lists evidence snippets.                                                                                                       |


## Diagnosis

Primary issue: **generation/prompt failure**. The model did not synthesize an answer, despite retrieving the broadly correct pages.

Secondary issue: **retrieval/chunking or reranking weakness**. The correct page is present, but the cited p. 14 evidence cuts off just before the crucial lines 503–510. Reranking also allowed an unrelated p. 3 citation into the top evidence. OCR is not the cause; the source page clearly contains the needed wording.

## Overall assessment

This is a near miss at the page-retrieval level but a failed QA response. A good answer should have said: **Thetis asks Zeus to honor Achilles by giving strength to the Trojans until the Achaians are forced to restore Achilles’ rights/honor and increase his honor among them.**

## Q6. What does Hera suspect Zeus has done?

**Test set:** B — Speaker/action attribution

### Expected

- Expected evidence: p. 16
- Good answer should mention: Hera suspects Zeus was persuaded by Thetis to honour Achilles and harm the Achaians.
- Failure signs: Attributes Hera’s suspicion to Achilles; says Achilles criticizes Zeus.

### Investigator response

```md
Question: What does Hera suspect Zeus has done?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 15] 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke revilingly to Zeus son of Kronos: 'Tr...
- [p. 16] 565 But go then, sit down in silence, and do as I tell you, for fear all the gods, as many as are on Olympos, can do nothing if I come close and lay my unconquerable hands upon you.' He spoke, and the goddcss the ox-eyed lady Hera was frigh...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 15 | p0015_c01] 535 Thus he took his place on the throne; yet Hera was not ignorant, having seen how he had been plotting counsels with Thetis the silver-footed, the daughter of the sea's ancient, and at once she spoke revilingly to Zeus son of Kronos: 'Treacherous one, what god has been plotting counsels with you?
- [p. 16 | p0016_c01] 565 But go then, sit down in silence, and do as I tell you, for fear all the gods, as many as are on Olympos, can do nothing if I come close and lay my unconquerable hands upon you.' He spoke, and the goddcss the ox-eyed lady Hera was frightened and went and sat down in silence wrenching her heart to obedience, 57o and all the Uranian gods in the house of Zeus werc troubled.
```

### Subagent evaluation

**Question:** What does Hera suspect Zeus has done?

## Expected answer

Hera suspects Zeus has been won over/persuaded by Thetis to honor Achilles and harm the Achaians, specifically by destroying many beside the Achaian ships.

## Lightweight checks

- **Expected page:** p. 16.
- **Expected page retrieved/cited:** Yes, but the cited p. 16 chunk starts at line 565 and misses the decisive lines just above it: “I am terribly afraid you were won over / by Thetis...” and “to do honour / to Achilleus, and to destroy many...”
- **Other citations:** p. 15 is partially relevant as setup: Hera saw Zeus “plotting counsels with Thetis.” p. 3 is irrelevant.
- **Missing citation issue:** The key answer-bearing p. 16 lines 553-558 are absent from the displayed evidence.
- **Forbidden failure signs:** Does not attribute the suspicion to Achilles and does not say Achilles criticizes Zeus. However, it also does not produce the required direct answer.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                    |
| ------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | Retrieved the expected page and related p. 15 setup, but the exact answer span was not included; p. 3 is noise.                                          |
| citation_accuracy   | 2/5   | p. 15 supports the context of Zeus consulting Thetis, but the p. 16 citation shown does not support the answer because it begins after Hera’s suspicion. |
| speaker_attribution | 2/5   | Evidence implies Hera is speaking to Zeus on p. 15, but the response never states Hera’s suspicion directly.                                             |
| causal_chain        | 1/5   | Does not connect Thetis persuading Zeus → honoring Achilles → harming/destroying Achaians.                                                               |
| no_hallucination    | 4/5   | No major fabricated claim, but the output is mostly non-answering evidence and includes irrelevant p. 3.                                                 |
| answer_quality      | 1/5   | Fails to answer the question in prose; only lists evidence snippets, and the crucial snippet is missing.                                                 |


## Diagnosis

- **Retrieval/reranking:** Mixed. It located p. 16 and p. 15, but the selected p. 16 chunk is shifted too late. The reranker/chunker failed to prioritize the exact “won over by Thetis... honour Achilleus... destroy many...” passage.
- **Generation:** Main failure. The model did not synthesize a direct answer from the retrieved evidence and instead emitted a “Best evidence” list.
- **Prompting:** Likely encourages evidence-first output too strongly or does not force a concise answer before citations.
- **OCR:** Not a significant blocker. There are minor OCR errors (`SSS` for 555, `goddcss`), but the key p. 16 text is readable.

## Suggested improvements

1. Require the final response to begin with a direct one-sentence answer, followed by citations.
2. Expand chunk windows or include neighboring lines around top page hits, especially when a cited chunk starts immediately after a likely answer span.
3. Penalize irrelevant early-book matches like p. 3 when the query contains named entities Hera/Zeus/Thetis or asks a localized speaker-action question.
4. Add a citation validation step: cited evidence must contain the answer terms or close paraphrase (`Thetis`, `honour Achilleus`, `destroy many/Achaians`).

## Q7. Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 1–12
- Good answer should mention: 1. Chryses asks for daughter back. 2. Agamemnon refuses. 3. Apollo sends plague. 4. Kalchas explains cause. 5. Agamemnon demands compensation. 6. Agamemnon takes Briseis. 7. Achilles withdraws and appeals to Thetis.
- Failure signs: Skips Kalchas; skips Briseis; treats Achilles’ withdrawal as random anger.

### Investigator response

```md
Question: Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 11] Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons...
Evidence:
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 11 | p0011_c01] Then Chryses, priest of him who strikes from afar, Apollo, 370 came beside the fast ships of the bronze-armoured Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, but above all Atreus' two sons, the marshals of the people.
```

### Subagent evaluation

## Question

Trace the chain of events from Chryses’ request to Achilles’ withdrawal from the fighting.

## Lightweight checks

- **Expected coverage:** pp. 1–12.
- **Retrieved/cited pages:** p. 1, p. 8, p. 11.
- **Missing key citations:** p. 2 (Agamemnon drives Chryses away; Chryses prays; Apollo sends plague), p. 3 (Achilles calls assembly; Kalchas explains cause), p. 4 (Agamemnon demands compensation), p. 6 (Agamemnon threatens to take Briseis), pp. 9–10 (Briseis actually taken; Achilles withdraws/weeps and calls Thetis).
- **Forbidden failure signs:**
  - Skips Kalchas: **mostly yes**. p. 11 alludes to “the seer,” but the answer does not identify Kalchas or his role clearly.
  - Skips Briseis: **partly**. Briseis appears only in p. 11 evidence; the answer does not explain her seizure as the trigger.
  - Treats withdrawal as random anger: **not explicitly**, but because no chain is synthesized, the causal connection is unclear.
- **Citation format:** citations are present, but the response gives “Best evidence” snippets rather than an actual traced answer.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                             |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | p. 1 and p. 11 are relevant; p. 8 is marginal. The result misses several essential pages for the chain.                                           |
| citation_accuracy   | 3/5   | The cited text is accurate to the OCR pages, but citations do not support a complete answer and p. 11 is a retrospective summary without context. |
| speaker_attribution | 1/5   | The response does not identify who is speaking in p. 11 or distinguish Chryses, Agamemnon, Kalchas, Achilles, and Thetis.                         |
| causal_chain        | 1/5   | It does not trace the sequence; it only lists snippets. Major causal links are omitted.                                                           |
| no_hallucination    | 5/5   | No clear invented claims; the problem is omission/non-answer.                                                                                     |
| answer_quality      | 1/5   | Fails the task: no coherent narrative chain, no synthesis, and missing required steps.                                                            |


## Diagnosis

- **Retrieval/reranking issue:** Top evidence under-covers the required span. The query needs multiple sequential events, but retrieval selected a beginning page, a later recap, and an only tangential Nestor page. It missed direct event pages with the plague, Kalchas, compensation demand, Briseis seizure, and Achilles’ withdrawal.
- **Generation issue:** The model did not answer the question; it returned evidence snippets. Even with the available p. 11 recap, it could have produced a partial chain but failed to synthesize.
- **Prompt issue:** The prompt likely allows “Best evidence” output to substitute for a response. For cause-and-effect questions, it should require an ordered chain with cited steps.
- **OCR issue:** Minor OCR errors exist (e.g., `I0`, `Briseus' daughter`, `takc/hcrc`), but they are not the main failure.

## Suggested improvements

1. For “trace the chain” questions, retrieve a wider contiguous page window around high-scoring hits, especially pp. 1–11 here.
2. Add a reranking objective for coverage of required entities/events: Chryses, Agamemnon, Apollo/plague, Kalchas, compensation/prize, Briseis, Achilles/Thetis.
3. Require generated answers to use an ordered list or arrow chain, with each step tied to a citation.
4. Add a post-generation checklist: if Kalchas or Briseis is missing, revise before finalizing.
5. Distinguish “Evidence” from “Response” in the prompt so the final answer cannot be only retrieved snippets.

## Q8. How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 3–10
- Good answer should mention: Agamemnon must return Chryseis but demands another prize; he threatens/takes Briseis from Achilles as compensation.
- Failure signs: Says Briseis belongs to Agamemnon originally; says Achilles takes Chryseis.

### Investigator response

```md
Question: How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?
Response: Best evidence:
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
Evidence:
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 9 | p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

## Question

How does the quarrel between Achilles and Agamemnon move from a dispute over Chryseis to a dispute over Briseis?

## Expected answer

Agamemnon must return Chryseis to end Apollo's plague, but he demands another prize so he will not be left without honor/compensation. When Achilles objects that prizes have already been distributed and accuses him of greed, Agamemnon threatens to take another leader's prize, specifically Achilles' Briseis, and later sends heralds to take her.

## Lightweight checks

- **Expected pages:** pp. 3–10.
- **Cited pages in result:** p. 8 and p. 9 only.
- **Missing key citations:**
  - **p. 4:** Agamemnon agrees to return Chryseis but demands a replacement prize; threatens to take Achilles', Aias', or Odysseus' prize if not compensated.
  - **p. 5:** Achilles objects and frames the threat as Agamemnon stripping away his own prize.
  - **p. 6:** Agamemnon explicitly says Apollo is taking Chryseis, so he will take Achilles' Briseis.
  - **p. 10:** Briseis is actually handed over and Achilles says Agamemnon has dishonored him by taking his prize.
- **Forbidden failure signs:** Not present. The response does **not** say Briseis belonged to Agamemnon originally and does **not** say Achilles takes Chryseis.
- **Citation format:** Present, but the top snippets are evidence-only and do not include the most direct causal bridge on p. 4/p. 6.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                                                    |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| retrieval_relevance | 3/5   | p. 9 is relevant because it shows Agamemnon ordering Briseis taken. p. 8 is only indirect context via Nestor's attempted mediation. The most important transition passages on pp. 4 and 6 are absent.                    |
| citation_accuracy   | 3/5   | The cited snippets are accurately quoted and page labels appear correct, but they under-support the full answer. p. 9 supports the final action, not the earlier Chryseis-to-compensation logic.                         |
| speaker_attribution | n/a   | The generated response provides no real prose answer attributing claims to speakers. The evidence itself identifies Nestor/Agamemnon, but attribution is not meaningfully tested.                                        |
| causal_chain        | 2/5   | The result shows the endpoint, Agamemnon sending for Briseis, but misses the causal steps: plague/Chryseis return → Agamemnon demands replacement prize → Achilles objects → Agamemnon targets Briseis.                  |
| no_hallucination    | 5/5   | No unsupported invented claims detected; the issue is omission rather than fabrication.                                                                                                                                  |
| answer_quality      | 2/5   | The response is mostly a pair of evidence snippets labeled “Best evidence,” not a synthesized answer to the question. It would not adequately answer the cause-and-effect prompt without the reader inferring the chain. |


## Diagnosis

- **Primary failure type:** Retrieval/reranking failure plus generation failure.
- **Retrieval/reranking:** The system retrieved p. 8 and p. 9, but missed or failed to rank higher the decisive p. 4 and p. 6 passages. p. 6 contains the clearest answer: “Even as Phoibos Apollo is taking away my Chryseis... I shall take the fair-cheeked Briseis, your prize.”
- **Generation:** The generated output does not synthesize the causal chain; it presents evidence snippets and leaves the answer implicit.
- **OCR:** No material OCR problem found. There are minor OCR artifacts (e.g., “takc,” “hcrc” on p. 6), but the relevant text remains readable and searchable enough in context.
- **Prompt:** The prompt or answer template may over-emphasize “best evidence” extraction and under-emphasize answering in prose with cited support.

## Suggested improvements

1. Add query expansion for causal-chain questions: include terms such as `Chryseis`, `Briseis`, `prize`, `take`, `give back`, `ransom`, `compensation`, and `threat`.
2. Improve reranking to prefer passages that contain both entities or the explicit transition sentence, especially p. 6.
3. Require a short synthesized answer before evidence bullets: e.g., “Because Agamemnon loses Chryseis, he demands compensation and chooses Achilles' Briseis.”
4. For multi-step questions, retrieve adjacent pages around top hits or merge page windows, since the chain spans pp. 4–10.
5. Add a prompt instruction to cite each causal step, not just the final action.

## Q9. Why does Achilles believe Agamemnon has dishonoured him?

**Test set:** C — Cause-and-effect chain

### Expected

- Expected evidence: pp. 5–12
- Good answer should mention: Achilles fights for Agamemnon/Menelaos’ cause, yet Agamemnon takes his prize; Briseis represents honour/status.
- Failure signs: Says Achilles is angry only because he loves Briseis romantically; misses honour/prize logic.

### Investigator response

```md
Question: Why does Achilles believe Agamemnon has dishonoured him?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
```

### Subagent evaluation

**Question:** Why does Achilles believe Agamemnon has dishonoured him?

## Lightweight checks

- **Expected pages:** pp. 5–12.
- **Retrieved/cited pages in result:** p. 3 and p. 1 only.
- **Expected-page hit:** **Fail** — no citation from the core relevant span, especially pp. 5–6 and pp. 10–12.
- **Missing key citations:**
  - p. 5: Achilles says he fights for Agamemnon/Menelaos though the Trojans have not wronged him; Agamemnon now threatens to strip away his prize.
  - p. 6: Agamemnon explicitly threatens to take Briseis, Achilles' prize, to demonstrate superiority.
  - p. 10: Achilles says Agamemnon has dishonoured him because he has taken away and keeps his prize.
  - p. 11–12: Achilles retells the causal chain to Thetis and asks that Agamemnon learn he did no honour to the best of the Achaians.
- **Forbidden failure signs:** The answer does **not** falsely say Achilles is angry only because he romantically loves Briseis, but it also does not explain the honour/prize logic.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                 |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 1/5   | Retrieved passages concern Chryses/Kalchas/Apollo and the beginning of the quarrel, not Achilles' stated reason for feeling dishonoured. They are only indirectly related background. |
| citation_accuracy   | 2/5   | The cited snippets are accurately located on p. 1 and p. 3, but they do not support the answer to this question. No support from the expected pages.                                  |
| speaker_attribution | n/a   | The response does not really make speaker claims about Achilles' belief; it mostly lists evidence snippets.                                                                           |
| causal_chain        | 0/5   | It misses the causal chain: Achilles fought for Agamemnon/Menelaos' honour, received Briseis as a prize/status marker, and Agamemnon dishonours him by threatening/taking that prize. |
| no_hallucination    | 4/5   | No obvious fabricated claim, but the response is effectively non-answering and could mislead by implying Chryses' dishonour is the relevant answer.                                   |
| answer_quality      | 1/5   | The result gives “Best evidence” rather than a direct explanation; it omits the central honour/prize logic and cites irrelevant pages.                                                |


## Qualitative assessment

This is a poor result for Q9. The evidence retrieved is about Apollo's plague and Agamemnon dishonouring Chryses, not about why Achilles believes Agamemnon dishonoured *him*. The response never states the correct answer: Achilles believes he has been dishonoured because he joined the war for Agamemnon/Menelaos' cause, did much of the fighting, received a prize from the Achaian distribution, and Agamemnon then threatened/took Briseis, that prize, as a public assertion of superiority.

## Likely failure source

- **Retrieval/reranking:** Primary failure. The system overmatched on the word “dishonoured” and retrieved the early Chryses passages on pp. 1 and 3 rather than Achilles' later complaints on pp. 5–12.
- **Generation:** Secondary failure. The generator did not compensate by forming an answer or noticing that the cited evidence concerned Chryses rather than Achilles.
- **OCR:** Not a major cause. Relevant OCR on pp. 5–12 is usable, though there are minor OCR errors on p. 6 such as “takc,” “hcr,” and “Briscis.”
- **Prompting:** Likely contributes if the prompt encourages returning top evidence even when evidence does not answer the question.

## Suggested improvements

1. Add query expansion/reranking terms for this question: “Achilles prize,” “Briseis,” “dishonoured me,” “taken away my prize,” “win your honour and Menelaos,” “best of the Achaians.”
2. Penalize or rerank passages where the dishonoured person is not the question target; here, “dishonoured Chryses” should not satisfy “dishonoured him” referring to Achilles.
3. Require answer generation to cite at least one passage that directly supports the claimed cause, preferably p. 5, p. 6, p. 10, or p. 11–12.
4. Add a self-check: if citations do not mention Achilles' prize/Briseis/honour, mark evidence insufficient rather than producing a best-evidence list.

## Q10. What is ironic about Achilles asking Zeus to help the Trojans?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 5, 12, 14–16
- Good answer should mention: Achilles is an Achaian warrior who fought against Troy, but because Agamemnon dishonoured him, he wants Trojan success so the Achaians suffer and recognize his value.
- Failure signs: Says Thetis asks Achilles to pray; says the irony is Zeus being suspicious; cites irrelevant p. 13.

### Investigator response

```md
Question: What is ironic about Achilles asking Zeus to help the Trojans?
Response: Best evidence:
- [p. 12] Sit beside him and take his knees and remind him of these things now, if perhaps he might be willing to help the Trojans, and pin the Achaians back against the ships and the water, dying, so that thus they may all have profit of their own k...
- [p. 15] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father,...
- [p. 14] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the mornin...
Evidence:
- [p. 12 | p0012_c01] Sit beside him and take his knees and remind him of these things now, if perhaps he might be willing to help the Trojans, and pin the Achaians back against the ships and the water, dying, so that thus they may all have profit of their own king, 410 that Atreus' son wide-ruling Agamemnon may recognize his madness, that he did no honour to the best of the Achaians.' Thetis answered him then letting the tears fall: 'Ah me, my child.
- [p. 15 | p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
- [p. 14 | p0014_c01] But when the twelfth dawn after this day appeared, the gods who live forever came back to Olympos all in a body and Zeus led them; nor did Thetis forget the entreaties 495 of her son, but she emerged from the sea's waves early in the morning and went up to the tall sky and Olympos.
```

### Subagent evaluation

## Question

What is ironic about Achilles asking Zeus to help the Trojans?

## Lightweight checks

- **Expected pages:** pp. 5, 12, 14–16.
- **Retrieved/cited pages in response:** pp. 12, 15, 14.
- **Missing expected citations:** p. 5 is missing; p. 16 is missing. These are important because p. 5 establishes Achilles as an Achaian fighting against Troy and explains his grievance against Agamemnon; p. 16 confirms the consequence Hera understands: honor Achilles by destroying many Achaians.
- **Irrelevant/forbidden p. 13 citation:** Not present.
- **Forbidden failure signs:**
  - Does **not** say Thetis asks Achilles to pray.
  - Does **not** say the irony is Zeus being suspicious.
  - Does **not** cite irrelevant p. 13.
- **Major answer-form issue:** The response gives “Best evidence” snippets but does not actually synthesize an answer explaining the irony.

## Source-grounded observations

- **p. 5:** Achilles says he did not come to fight the Trojans because they had harmed him personally; he came for Agamemnon/Menelaos’ honor, and now Agamemnon dishonors him by threatening/taking his prize. This is the key setup for the irony.
- **p. 12:** Achilles tells Thetis to ask Zeus to help the Trojans and pin the Achaians back against the ships so Agamemnon will recognize his madness and his dishonor of “the best of the Achaians.” This is highly relevant.
- **p. 14:** Thetis supplicates Zeus and asks him to strengthen the Trojans until the Achaians give Achilles his rights and increase his honor. Relevant.
- **p. 15:** Zeus agrees by nodding; relevant to the causal chain, though less directly to the irony than pp. 5, 12, 14, 16.
- **p. 16:** Hera understands Zeus has assented to honor Achilles and “destroy many beside the ships of the Achaians.” Relevant consequence, but not retrieved.

## Rubric scores


| Criterion           | Score | Rationale                                                                                                                                                                                                              |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 3/5   | Retrieved central pages 12 and 14, plus p. 15 for Zeus’s assent, but missed p. 5, which is essential for explaining the irony, and p. 16, which helps confirm consequences.                                            |
| citation_accuracy   | 4/5   | The cited snippets accurately match their pages and are not fabricated. However, p. 15 is somewhat secondary, and the citation set is incomplete for the expected answer.                                              |
| speaker_attribution | 2/5   | The response quotes material but does not identify that p. 12 is Achilles instructing Thetis or that p. 14 is Thetis speaking to Zeus. It avoids the forbidden misattribution, but leaves attribution implicit.        |
| causal_chain        | 2/5   | Evidence implies the chain: Agamemnon dishonors Achilles → Achilles asks Thetis/Zeus → Trojan success harms Achaians → Agamemnon recognizes Achilles’ value. But the answer does not explicitly explain it.            |
| no_hallucination    | 5/5   | No clear fabricated claims or forbidden claims. The response is under-answered rather than hallucinated.                                                                                                               |
| answer_quality      | 1/5   | It fails to answer the question in prose. It only lists evidence, omitting the direct explanation that Achilles is an Achaian warrior asking for Trojan success against his own side because Agamemnon dishonored him. |


## Diagnosis

- **Primary failure: generation/prompting.** The model produced an evidence list instead of a synthesized interpretive answer. The retrieved evidence was partially sufficient to answer, but the response never states the irony.
- **Secondary failure: retrieval/reranking.** The system missed p. 5, the strongest page for Achilles’ identity/allegiance and his statement that the Trojans had done him no personal harm. It also missed p. 16, a useful confirmation of Zeus’s destructive support against the Achaians.
- **OCR:** No major OCR issue affecting this question. There are minor OCR artifacts in the source pages, but the relevant lines are readable.
- **Prompt:** The prompt or output format may over-prioritize “Best evidence” extraction and under-prioritize answering the user’s question.

## Suggested improvements

1. Require the final response to include a concise answer sentence before evidence, e.g. “The irony is that Achilles, one of the greatest Achaian fighters against Troy, asks Zeus to help Troy because Agamemnon has dishonored him.”
2. Improve reranking for interpretive questions by prioritizing passages that establish both sides of the contrast: Achilles’ Achaian role/grievance on p. 5 plus his request to aid Trojans on p. 12.
3. Add a speaker-attribution instruction: identify who is speaking in quoted evidence when the quote is dialogue.
4. For causal questions, require an explicit causal chain linking grievance, divine request, Trojan success, Achaian suffering, and restoration of Achilles’ honor.

## Q11. How does Book 1 show that honour is both personal and political?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: pp. 1–16
- Good answer should mention: Personal insult to Chryses causes public plague; Agamemnon’s seizure of Briseis humiliates Achilles; Achilles’ anger harms the whole army; Thetis/Zeus turn the honour dispute into a war-level consequence.
- Failure signs: Only discusses Achilles’ emotions; ignores public/military consequences.

### Investigator response

```md
Question: How does Book 1 show that honour is both personal and political?
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
Evidence:
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** How does Book 1 show that honour is both personal and political?

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | Retrieved p. 1 is relevant for Chryses' dishonour causing plague. Retrieved p. 8 is only indirectly relevant (Nestor on kingly honour / Achilles as bulwark) and misses stronger pages: p. 5–7 for Achilles' prize/dishonour and threat to withdraw, p. 10–12 for Briseis taken and Achilles/Thetis requesting Trojan success, p. 14 for Achilles staying out of battle and Thetis asking Zeus to honour him by strengthening Trojans. |
| citation_accuracy   | 3/5   | The cited snippets accurately come from p. 1 and p. 8, but the answer does not use them to support a full claim. Citation set is incomplete for the expected causal chain.                                                                                                                                                                                                                                                             |
| speaker_attribution | n/a   | The response is evidence-only and makes almost no speaker claims. It does not misattribute speakers, but also does not identify Nestor/Agamemnon/Achilles/Thetis where useful.                                                                                                                                                                                                                                                         |
| causal_chain        | 1/5   | Captures only the first link: dishonouring Chryses leads Apollo to plague the host. It does not explain Agamemnon taking Briseis, Achilles' public humiliation/withdrawal, Thetis' appeal, or Zeus making the quarrel affect the whole war.                                                                                                                                                                                            |
| no_hallucination    | 5/5   | No unsupported invented claims; the problem is omission rather than hallucination.                                                                                                                                                                                                                                                                                                                                                     |
| answer_quality      | 1/5   | It gives two evidence bullets, not an interpretive answer. It fails the expected contrast between personal honour and political/military consequences.                                                                                                                                                                                                                                                                                 |


## Qualitative diagnosis

The response is mostly a retrieval failure compounded by generation/prompt behavior. The generator appears to have selected and printed the top evidence rather than synthesizing an answer. Page 1 is a good starting citation because Agamemnon's personal dishonouring of Chryses immediately becomes a public plague: Apollo drives pestilence through the host and people perish. However, the second citation from p. 8 is weak for this question. Nestor's speech does mention unequal kingly honour and calls Achilles a bulwark for all Achaians, but it does not by itself establish the full political consequence.

Important missed evidence includes:

- **p. 5:** Achilles says the army fought to win honour for Agamemnon and Menelaos, then complains that Agamemnon threatens to strip away his own prize and leave him dishonoured.
- **p. 6:** Agamemnon explicitly threatens to take Briseis, Achilles' prize, to prove he is greater.
- **p. 7:** Achilles predicts the Achaians will long for him when they die before Hektor, because Agamemnon failed to honour the best of the Achaians.
- **p. 10:** Briseis is taken; Achilles says Agamemnon has dishonoured him and warns the Achaians may need him to avert destruction.
- **p. 12:** Achilles asks Thetis to persuade Zeus to help the Trojans and pin the Achaians against the ships until Agamemnon recognizes that he dishonoured Achilles.
- **p. 14:** Achilles stays away from assembly and battle; Thetis asks Zeus to honour Achilles by strengthening the Trojans until the Achaians increase his honour.

## Suggested improvements

1. **Retrieve more chunks / diversify query terms:** include terms such as `honour`, `dishonoured`, `prize`, `Briseis`, `Achaians perish`, `Thetis Zeus`, and `Trojans` so later consequences are retrieved, not just the opening plague.
2. **Use multi-hop/context expansion:** after retrieving p. 1, expand around pages 5–14 where the same honour dispute develops into Achilles' withdrawal and Zeus' intervention.
3. **Improve reranking for causal coverage:** prefer evidence sets that cover both personal insult and collective military outcome; avoid returning two nearby/partial thematic citations when the question asks for an interpretive chain.
4. **Prompt generation to synthesize, not list evidence:** require a short thesis plus 3–4 cited causal steps. For this question, a good answer should say that private status injuries become public political crises: Chryses' slight brings plague, Achilles' loss of Briseis shames him, his withdrawal endangers the army, and Thetis/Zeus convert the insult into Trojan advantage.
5. **OCR is not the main issue:** there are minor OCR errors (`I0`, `takc`, `hcr`, `goo`, `sos`), but relevant passages are readable enough. The failure is primarily retrieval/reranking and answer-generation format.

## Q12. How does Nestor try to resolve the conflict between Achilles and Agamemnon?

**Test set:** D — Interpretive but source-grounded

### Expected

- Expected evidence: p. 8
- Good answer should mention: Nestor urges restraint; acknowledges Achilles’ strength but Agamemnon’s greater authority; tries to preserve unity among the Achaians.
- Failure signs: Says Nestor takes Achilles’ side completely; says he orders Agamemnon to return Briseis.

### Investigator response

```md
Question: How does Nestor try to resolve the conflict between Achilles and Agamemnon?
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 9 | p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

**Question:** How does Nestor try to resolve the conflict between Achilles and Agamemnon?

## Rubric Scores


| Criterion           | Score | Notes                                                                                                                                                                                                                        |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 1/5   | Retrieved p. 3 and p. 9, but the required Nestor mediation passage is on p. 8. p. 9 is only indirectly relevant as aftermath; p. 3 is unrelated to Nestor.                                                                   |
| citation_accuracy   | 2/5   | The cited snippets accurately reflect their pages, but they do not support an answer about Nestor's intervention. Missing the key citation to p. 8 lines 253-284.                                                            |
| speaker_attribution | n/a   | The response gives evidence snippets only and does not actually attribute Nestor's speech or claims. If treated as an answer, it omits Nestor entirely.                                                                      |
| causal_chain        | 0/5   | Does not explain Nestor's strategy: shame both men, warn that Trojans benefit from Achaian division, urge both to obey counsel, tell Agamemnon not to take Briseis, and tell Achilles not to challenge the king's authority. |
| no_hallucination    | 5/5   | No unsupported claims are made; the problem is omission/non-answer rather than hallucination.                                                                                                                                |
| answer_quality      | 0/5   | The output is not an answer to the question. It provides irrelevant/weak evidence and never states how Nestor tries to resolve the quarrel.                                                                                  |


## What the source says

On **p. 8**, Nestor rises "in kind intention toward both" after Achilles and Agamemnon rage at each other. He says their quarrel brings sorrow to Achaia and would delight Priam and the Trojans. He asks both younger men to be persuaded by him. His concrete mediation is balanced:

- to **Agamemnon**: "do not take the girl away / but let her be," since Briseis was Achilles' prize from the Achaians;
- to **Achilles**: do not try to match strength with the king, because the sceptred king has greater honor and rules more men;
- to **Agamemnon again**: give up anger against Achilles, who is a great bulwark for the Achaians.

A good answer should say Nestor tries to preserve Achaian unity through compromise and restraint, recognizing Achilles' strength while also acknowledging Agamemnon's higher authority.

## Diagnosis

- **Retrieval/reranking failure:** The system failed to retrieve/rank the central p. 8 Nestor passage despite the question naming Nestor. The retrieved pages are adjacent narrative context but not the answer-bearing passage.
- **Generation failure / prompt weakness:** The generated response appears to stop at "Best evidence" and does not synthesize an answer. It should have either refused due to missing evidence or produced a concise answer only if supported.
- **OCR issue:** Not a major factor. Page 8 OCR is clean enough and contains the needed terms: "Nestor," "obey," "do not take the girl away," "son of Peleus," "sceptred king," and "give up your anger."

## Suggested improvements

1. Boost retrieval for named characters and direct speech around the character name; query terms should include `Nestor`, `Achilleus`, `Agamemnon`, `resolve/quarrel/conflict`, and `anger`.
2. Add neighboring-page expansion when a retrieved page is near the expected scene; p. 7 introduces Nestor at the bottom and p. 8 contains his speech.
3. Rerank passages by direct answer cues, especially imperative mediation language: "do not take," "do not match," "give up your anger," "be persuaded."
4. Strengthen the answer prompt to require a direct response before evidence and to avoid returning evidence-only outputs.
5. If answer-bearing evidence is absent, require the model to state insufficiency rather than cite irrelevant passages.

## Q13. Find evidence that Agamemnon’s leadership damages the Achaian army.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–5, 8–12
- Good answer should mention: His rejection of Chryses brings plague; his demand for compensation creates conflict with Achilles; taking Briseis leads Achilles to withdraw.
- Failure signs: Retrieves only p. 8 or only p. 1; does not connect multiple events.

### Investigator response

```md
Question: Find evidence that Agamemnon’s leadership damages the Achaian army.
Response: Best evidence:
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
Evidence:
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 9 | p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
```

### Subagent evaluation

**Question:** Find evidence that Agamemnon’s leadership damages the Achaian army.

## Scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| retrieval_relevance | 4/5   | Retrieved relevant pages for Kalchas/plague explanation (p. 3), Nestor warning about Achilles as Achaian bulwark (p. 8), and Agamemnon ordering Briseis taken (p. 9). However it missed very strong direct evidence on pp. 1–2 for Agamemnon rejecting Chryses and Apollo's plague, and p. 10/p. 11 for Achilles explicitly linking Briseis to future Achaian destruction/perishing. |
| citation_accuracy   | 5/5   | Cited snippets match the source pages and page numbers. No apparent page mis-citation.                                                                                                                                                                                                                                                                                               |
| speaker_attribution | 2/5   | The answer does not clearly identify who is speaking. p. 3 includes Achilles then Kalchas; p. 8 is Nestor; p. 9 is narrator plus Agamemnon’s order. Attribution is only recoverable from quoted text, not explained by the answer.                                                                                                                                                   |
| causal_chain        | 2/5   | It gives fragments but does not connect the full chain: Agamemnon dishonors Chryses → Apollo sends plague → Agamemnon demands compensation/conflicts with Achilles → Agamemnon takes Briseis → Achilles withdraws, harming the army.                                                                                                                                                 |
| no_hallucination    | 5/5   | No unsupported invented claims found; the problem is omission and weak synthesis, not hallucination.                                                                                                                                                                                                                                                                                 |
| answer_quality      | 2/5   | The response is mostly raw/partial evidence snippets. It does not directly answer the abstract prompt or explain how the evidence proves damaged leadership.                                                                                                                                                                                                                         |


## Key source evidence that should have been used

- **pp. 1–3:** Agamemnon dishonors Chryses, refuses ransom, and Apollo sends plague; Kalchas states the plague is because Agamemnon dishonored the priest and would not return Chryseis.
- **pp. 4–5:** Agamemnon admits he wants his people safe but immediately demands a replacement prize, escalating conflict with Achilles.
- **pp. 7–8:** Achilles calls Agamemnon a ruler who feeds on his people; Nestor warns that quarrelling brings sorrow to Achaia and urges Agamemnon not to take Briseis because Achilles is a “great bulwark of battle.”
- **pp. 9–10:** Agamemnon follows through by sending heralds to take Briseis; Achilles says future Achaian destruction will need him and that Agamemnon lacks foresight so the Achaians may perish.
- **p. 11:** Achilles recounts the full causal chain: Chryses rejected, Apollo’s arrows kill Achaians, Agamemnon threatens Achilles, and Briseis is taken.

## Diagnosis

- **Retrieval/reranking:** Partially successful but under-diverse. It found relevant middle-chain passages but did not surface the opening plague/rejection pages or the later explicit withdrawal/destruction passage strongly enough. For this abstract query, retrieval should favor coverage across the event chain rather than topically similar isolated snippets.
- **Generation:** Main failure. The generated answer did not synthesize evidence or state causal links. It should have converted snippets into a compact argument with cited support.
- **Prompting:** Likely needs instruction for abstract/evidence questions: “identify 2–4 connected events, cite each, and explain how each damages the army.”
- **OCR:** Not a major issue. OCR has minor line-number confusions (`I00`, `I25`, etc.) and a few character errors, but the relevant text is readable.

## Suggested improvements

1. Add a multi-hop/coverage reranking step for abstract questions: require evidence from early plague cause, conflict escalation, and Achilles/Briseis consequences.
2. Increase retrieval diversity by page/window, avoiding three snippets clustered around only the argument aftermath.
3. Prompt generation to produce an explanatory causal chain, not just “best evidence” excerpts.
4. Prefer broader adjacent windows for epic narrative passages so the cause and consequence stay together.

## Q14. Find evidence that divine power responds to human dishonour in Book 1.

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 1–3, 12, 14–16
- Good answer should mention: Apollo punishes Agamemnon’s dishonour of Chryses; Achilles/Thetis appeal to Zeus over Achilles’ dishonour.
- Failure signs: Mentions gods vaguely without explaining the human action that triggers divine response.

### Investigator response

```md
Question: Find evidence that divine power responds to human dishonour in Book 1.
Response: Best evidence:
- [p. 1] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delica...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 2] 35 Over and over the old man prayed as he walked in solitude to King Apollo, whom Leto of the lovely hair bore: 'Hear me, lord of the silver bow who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos...
Evidence:
- [p. 1 | p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 2 | p0002_c01] 35 Over and over the old man prayed as he walked in solitude to King Apollo, whom Leto of the lovely hair bore: 'Hear me, lord of the silver bow who set your power about Chryse and Killa the sacrosanct, who are lord in strength over Tenedos, Smintheus, if ever it pleased your heart that I built your temple, 40 if ever it pleased you that I burned all the rich thigh pieces of bulls, of goats, then bring to pass this wish I pray for: let your arrows make the Danaans pay for my tears shed.' So he s...
```

### Subagent evaluation

**Question:** Find evidence that divine power responds to human dishonour in Book 1.  
**Expected evidence:** Apollo punishes the Achaeans because Agamemnon dishonours Chryses; Achilles/Thetis appeal to Zeus because Agamemnon dishonours Achilles.

## Scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                                                       |
| ------------------- | ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | Retrieves strong Apollo evidence on pp. 1–2, but includes irrelevant p. 8 and misses the Achilles/Thetis/Zeus evidence on pp. 10–12 and 14–16.                                                                                                                              |
| citation_accuracy   | 3/5   | Page citations are real and quoted text appears to match the source. However p. 8 does not support the requested claim, and the answer relies on truncated snippets rather than precise supporting lines.                                                                   |
| speaker_attribution | 2/5   | Does not identify key speakers clearly. p. 2 is Chryses praying to Apollo; p. 14 is Thetis supplicating Zeus, but the latter is absent. p. 8 attribution/context is not useful.                                                                                             |
| causal_chain        | 2/5   | Partly shows the Apollo chain: Agamemnon dishonours Chryses → Chryses prays → Apollo sends plague. It fails to show the second required chain: Agamemnon dishonours Achilles → Achilles asks Thetis → Thetis asks Zeus → Zeus agrees to honour Achilles by helping Trojans. |
| no_hallucination    | 4/5   | No major fabricated claims, but the p. 8 evidence is a misleading/irrelevant inclusion.                                                                                                                                                                                     |
| answer_quality      | 2/5   | The response is mostly a list of snippets. It does not directly answer the abstract question or synthesize the two examples of divine response to dishonour.                                                                                                                |


## Source check

Relevant source passages:

- **pp. 1–3:** The narrator states Apollo drove plague through the army because Agamemnon dishonoured Chryses (p. 1). Chryses prays for Apollo to make the Danaans pay for his tears, and Apollo hears him and shoots the plague arrows (p. 2). Kalchas later confirms Apollo blames them because Agamemnon dishonoured his priest and refused ransom (p. 3).
- **pp. 10–12:** Achilles says Agamemnon has dishonoured him by taking Briseis (p. 10), asks Thetis to supplicate Zeus (p. 11), and asks that Zeus help the Trojans so Agamemnon recognizes that he “did no honour to the best of the Achaians” (p. 12).
- **pp. 14–16:** Thetis does supplicate Zeus, explicitly saying Agamemnon dishofanoured Achilles and asking Zeus to honour him by strengthening the Trojans until the Achaeans restore Achilles’ rights (p. 14). Zeus silently agrees with a nod (p. 15), and Hera understands that Zeus has agreed to honour Achilles and destroy many Achaeans by the ships (p. 16).

## Diagnosis

- **Retrieval/reranking issue:** The system retrieved the early Apollo material but failed to retrieve or rank the later Thetis/Zeus material, despite expected pages including 12 and 14–16. p. 8 is a near-topic but poor match about honour/status, not divine response.
- **Generation issue:** The answer did not transform evidence into an explanation. It should explicitly connect human dishonour to divine action in two causal chains.
- **Prompt issue:** The model may need instruction to answer abstract theme questions by identifying multiple episodes and explaining causality, not merely returning top snippets.
- **OCR issue:** OCR has minor artifacts (`S ING`, `I0`, `goo`, `sos`), but the relevant content is readable. OCR is not the main failure.

## Suggested improvements

1. Improve reranking for abstract queries by rewarding passages containing both dishonour/honour language and divine response verbs/actions (`heard`, `prayed`, `sent`, `plague`, `Zeus`, `Thetis`, `do honour`).
2. Add adjacent-page expansion around high-value hits: a hit on Achilles’ dishonour around p. 10 should pull pp. 11–12 and 14–16 into context.
3. Prompt generation to produce a concise thematic synthesis: “name the human dishonour, name the god, describe the divine response, cite pages.”
4. Penalize evidence that discusses honour only socially/politically without divine intervention, such as p. 8 here.

## Q15. What role does Briseis play in the conflict, beyond being a captured woman?

**Test set:** E — Retrieval difficulty / abstract query

### Expected

- Expected evidence: pp. 6–10, 11–12
- Good answer should mention: Briseis functions as Achilles’ prize and symbol of honour; Agamemnon taking her publicly humiliates Achilles and triggers his withdrawal.
- Failure signs: Reduces Briseis only to romance; gives unsupported character analysis.

### Investigator response

```md
Question: What role does Briseis play in the conflict, beyond being a captured woman?
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 9] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to...
- [p. 10] 345 He led forth from the hut Briseis of the fair cheeks and gave her to be taken away; and they walked back beside the ships of the Achaians, and the woman all unwilling went with them still.
Evidence:
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 9 | p0009_c01] But Agamemnon did not give up his anger and the first threat he made to Achilleus, but to Talthybios he gave his orders and Eurybates 320 who were heralds and hard-working henchmen to him: 'Go now to the shelter of Peleus' son Achilleus, to bring back Briseis of the fair cheeks leading her by the hand.
- [p. 10 | p0010_c01] 345 He led forth from the hut Briseis of the fair cheeks and gave her to be taken away; and they walked back beside the ships of the Achaians, and the woman all unwilling went with them still.
```

### Subagent evaluation

**Question:** What role does Briseis play in the conflict, beyond being a captured woman?

## Verdict

The result retrieves some directly relevant Briseis passages but does **not actually answer the interpretive question**. It mostly returns excerpts, including one irrelevant opening plague passage. It misses or underuses the crucial honor/prize framing on pp. 5–6 and Achilles’ explicit explanation on pp. 10–12.

## Rubric


| Check               | Score | Notes                                                                                                                                                                                                            |
| ------------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 3/5   | p. 9 and p. 10 are relevant to Briseis being taken; p. 1 is mostly irrelevant. Missing strongest support: p. 5 lines 161–170, p. 6 lines 181–187, p. 10 lines 353–355, p. 11 lines 386–391, p. 12 lines 427–430. |
| citation_accuracy   | 4/5   | The cited snippets from p. 1, p. 9, and p. 10 match the OCR/source pages. Citation page labels appear accurate. Point lost because citation selection does not substantiate the full answer expected.            |
| speaker_attribution | n/a   | The response gives no substantive speaker-based claims beyond quoted source snippets. If assessed implicitly, it does not misattribute speakers.                                                                 |
| causal_chain        | 1/5   | It does not explain that Briseis is Achilles’ prize/sign of honor, that Agamemnon seizes her to assert superiority, and that this public dishonoring causes Achilles’ withdrawal.                                |
| no_hallucination    | 5/5   | No unsupported claims are introduced; the problem is omission/non-answer rather than fabrication.                                                                                                                |
| answer_quality      | 1/5   | The response is evidence-only and fails to synthesize the role Briseis plays. It would not satisfy the user’s abstract/interpretive question.                                                                    |


## What a good answer should have said

Briseis is not merely a captive woman; she is Achilles’ allotted war-prize and therefore a visible token of his honor among the Achaians. Agamemnon’s decision to take her is a deliberate assertion that he is “greater” than Achilles (p. 6), and Achilles interprets it as being dishonored because Agamemnon “has taken away my prize and keeps it” (p. 10). This humiliation leads Achilles to withdraw from battle and ask Thetis to have Zeus punish the Achaians until Agamemnon recognizes that he dishonored “the best of the Achaians” (pp. 11–12).

## Diagnosis

- **Retrieval/reranking issue:** The result surfaced p. 9–10 but failed to rank p. 5–6 highly enough, where the prize/honor logic is explicit. It also included p. 1, which is background for Chryseis/Apollo but not directly about Briseis’ role.
- **Generation/prompt issue:** The model output “Best evidence” rather than a synthesized response. It did not bridge from evidence to interpretation.
- **OCR issue:** Minor OCR noise exists on p. 6 (`takc`, `angcr`, `hcrc`, `Briscis`), which could weaken lexical matching for “Briseis,” “take,” and “anger,” but the passage is still readable.
- **Citation coverage issue:** The selected evidence supports the event of seizure, but not enough of the symbolic/causal meaning.

## Suggested improvements

1. Add query expansion/reranking terms for abstract questions: `prize`, `honour/honor`, `dishonoured`, `gift of the Achaians`, `outrage`, `withdraw`, `stay away from fighting`.
2. Prefer contiguous context around retrieved Briseis mentions, especially preceding lines where Achilles discusses prizes and honor.
3. Penalize generic opening/background chunks when the question asks specifically about Briseis.
4. Strengthen the generation prompt: require a direct 2–4 sentence answer first, then evidence; prohibit evidence-only responses.
5. Consider OCR normalization for common errors (`Briscis` → `Briseis`, `takc` → `take`) before indexing or during query expansion.

## Q16. Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16
- Good answer should mention: Opening invocation, Apollo’s plague, Achilles/Agamemnon quarrel, Briseis, Thetis/Zeus.
- Failure signs: Over-focuses on one scene; weak citations; no chain of causality.

### Investigator response

```md
Question: Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?
Response: Best evidence:
- [p. 1] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to...
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
Evidence:
- [p. 1 | p0001_c01] Zeus' son and Leto's, Apollo, who in anger at the king drove the foul pestilence along the host, and the people perished, I0 since Atreus' son had dishonoured Chryses, priest of Apollo, when he came beside the fast ships of the Achaians to ransom back his daughter, carrying gifts beyond count and holding in his hands wound on a staff of gold the ribbons of Apollo who strikes from afar, and supplicated all the Achaians, 15 but above all Atreus' two sons, the marshals of the people: 'Sons of Atreu...
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
```

### Subagent evaluation

**Question:** Write a 300-word answer: How does Book 1 present the relationship between anger, honour, and military disaster?

## Verdict

The result is **not an answer to the essay prompt**. It returns two evidence snippets rather than a 300-word synthesis. The retrieved pages are relevant but far too narrow: p. 1 supports the opening chain from dishonour to Apollo's plague, and p. 8 supports Nestor's warning about anger and Achilles as the Achaian bulwark. However, the response misses the central continuation of the causal chain: Agamemnon's demand for a replacement prize, the seizure of Briseis, Achilles' withdrawal, his appeal to Thetis, and Thetis/Zeus arranging future Achaian losses.

## Lightweight checks

- **Uses enough pages:** No. It cites only **2 pages** (pp. 1 and 8) despite the expected range **pp. 1–16** and the question requiring a Book-wide causal argument.
- **Citations support claims:** The two citations are accurate and relevant, but there are almost no claims to support because the output is evidence-only.
- **Avoids broad unsupported phrases:** Mostly yes because it avoids broad interpretive claims altogether; the failure is omission rather than unsupported overreach.

## Rubric


| Criterion           | Score | Notes                                                                                                                                            |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| retrieval_relevance | 2/5   | Retrieved snippets are relevant but insufficient; misses Briseis, Achilles' withdrawal, Thetis, Zeus, and final military-disaster setup.         |
| citation_accuracy   | 4/5   | The cited p. 1 and p. 8 passages accurately match source text and support limited points about anger/dishonour.                                  |
| speaker_attribution | n/a   | No substantive answer or speaker claims; p. 8 context is Nestor, but the response does not identify him.                                         |
| causal_chain        | 1/5   | Starts with Apollo's plague and gestures toward anger, but does not build the required chain from honour dispute to future battlefield disaster. |
| no_hallucination    | 5/5   | No apparent fabricated content; the response is just incomplete.                                                                                 |
| answer_quality      | 1/5   | Fails the requested 300-word essay format and omits most required content.                                                                       |


## Diagnosis

- **Retrieval/reranking:** Under-retrieved for an essay-style question. It selected early plague evidence and Nestor's mediation but missed key later passages: Agamemnon threatening/taking Briseis (pp. 5–10), Achilles' dishonour complaint and withdrawal (pp. 10–12), and Thetis/Zeus causing future Achaian losses (pp. 12–16).
- **Generation:** Major failure. The system produced an evidence list rather than composing the requested answer.
- **OCR:** Not a major blocker. Some OCR noise exists (e.g., line numbers as `I0`, `goo`, `SSS`), but relevant passages remain readable.
- **Prompting:** The prompt likely needs stronger instructions for essay mode: synthesize across multiple citations, cover the expected motifs, and do not stop after evidence extraction.

## Suggested improvements

1. For essay questions, increase retrieval breadth/top-k and enforce page diversity across the expected page range.
2. Add query expansion terms: `Briseis`, `dishonoured`, `prize`, `Thetis`, `Zeus`, `Trojans`, `Achaians perish`, `bulwark of battle`.
3. Rerank for causal coverage, not just lexical relevance: plague → quarrel over prizes/honour → Briseis → Achilles withdraws → Thetis asks Zeus → Achaian disaster.
4. Add an answer-format guardrail: if the user asks for 300 words, produce a prose answer with citations, not only evidence snippets.
5. Encourage 4–6 citations for Book-wide essay answers, with at least one citation from the ending Thetis/Zeus section.

## Q17. Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–16
- Good answer should mention: Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, Hera.
- Failure signs: Omits Chryses/Kalchas; confuses speakers; cites loosely.

### Investigator response

```md
Question: Write a 500-word answer: In Book 1, how do priests, prophets, warriors, kings, and gods each shape the conflict?
Response: Best evidence:
- [p. 1] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delica...
- [p. 15] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father,...
Evidence:
- [p. 1 | p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 15 | p0015_c01] 530 So these two who had made their plans separated, and Thetis leapt down again from shining Olympos into the sea's depth, but Zeus went back to his own house, and all the gods rose up from their chairs to greet the coming of their father, not one had courage to keep his place as the father advanced, but stood up to greet him.
```

### Subagent evaluation

## Case

Question asks for a ~500-word synthesis of how priests, prophets, warriors, kings, and gods shape the conflict in Book 1, expected to use pp. 1–16 and mention Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, and Hera.

## Investigator result checked

The returned answer is not an essay. It provides only two evidence snippets:

- p. 1: opening invocation and initial cause: Achilles' anger, conflict with Agamemnon, Apollo's plague after Agamemnon dishonors Chryses.
- p. 15: aftermath of Zeus and Thetis' plan, Zeus returning to the gods.

## Lightweight checks

- **Uses enough pages:** No. Only 2 cited pages (p. 1 and p. 15) from an expected range of pp. 1–16. It misses central pages for Kalchas (p. 3), Achilles/Agamemnon escalation (pp. 4–10), Thetis' appeal (pp. 10–12, 14–15), and Hera's reaction (p. 15).
- **Includes required figures:** No. Evidence includes Achilles, Agamemnon, Chryses, Apollo, Zeus, Thetis in fragments, but omits Kalchas and Hera as substantive actors, and there is no generated prose explaining any figure.
- **Citations support claims:** Mostly not applicable because there are almost no claims. The cited snippets are relevant to beginning and Olympian end, but far too thin to support the requested causal overview.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                                                                                                                                                  |
| ------------------- | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| retrieval_relevance | 2/5   | p. 1 and p. 15 are relevant anchors, but retrieval misses most of the necessary chain and the named required figures, especially Kalchas and Hera.                                                                                                                                     |
| citation_accuracy   | 3/5   | The two snippets accurately come from the cited pages and support limited facts, but coverage is so incomplete that citations cannot support the requested answer.                                                                                                                     |
| speaker_attribution | n/a   | No actual essay/speaker claims to assess.                                                                                                                                                                                                                                              |
| causal_chain        | 1/5   | The result gestures at the opening cause and Zeus/Thetis endpoint but does not connect Chryses → Apollo plague → Achilles' assembly → Kalchas' prophecy → Agamemnon's compensation demand → Briseis seizure → Achilles' withdrawal → Thetis' supplication → Zeus/Hera divine conflict. |
| no_hallucination    | 5/5   | No unsupported invented content observed; failure is omission/non-answer rather than hallucination.                                                                                                                                                                                    |
| answer_quality      | 0/5   | Does not answer the prompt, is not ~500 words, and lacks synthesis.                                                                                                                                                                                                                    |


## Source-page observations

Useful support was available in OCR:

- **Chryses/priest:** pp. 1–2 and p. 11 show Chryses asking for his daughter, Agamemnon rejecting him, and Apollo answering his prayer with plague.
- **Kalchas/prophet:** p. 3 identifies Kalchas as seer and has him explain Apollo's anger and the need to return Chryseis with a hecatomb.
- **Achilles/warrior:** pp. 2–7 show Achilles calling assembly, protecting Kalchas, challenging Agamemnon, almost drawing his sword, and being restrained by Athene/Hera.
- **Agamemnon/king:** pp. 4–10 show Agamemnon demanding compensation, threatening and taking Briseis, and escalating the quarrel through royal authority.
- **Thetis/Zeus/Hera/gods:** pp. 10–15 show Achilles' appeal to Thetis, Thetis' plan to supplicate Zeus, Zeus' nod to honor Achilles by aiding Trojans, and Hera's suspicion/conflict with Zeus.

## Diagnosis

- **Retrieval/reranking failure:** The context set is far too narrow for an essay-style, multi-actor question. It retrieved only the opening and one late Olympian passage, not the middle pages carrying the key prophet and human-conflict chain.
- **Generation failure:** The generator did not produce an answer at all; it emitted a brief evidence list. This suggests the prompt/response mode may be optimized for short QA/evidence extraction and failed to switch into essay synthesis.
- **Prompt issue:** The instruction “Write a 500-word answer” was not enforced. The system likely needs explicit requirements: synthesize from multiple retrieved chunks, include required figures, cite each paragraph/claim.
- **OCR issue:** Not a major blocker. OCR has minor line-number errors (`I0`, `goo`, `sos`, `S50`) and some character substitutions, but the relevant names and content are readable.

## Suggested improvements

1. For essay questions, retrieve a larger and more diverse set of chunks/pages across the expected range, not just top-2 snippets.
2. Add entity/coverage constraints to retrieval or reranking: require evidence for Chryses, Kalchas, Achilles, Agamemnon, Thetis, Zeus, Hera before generation.
3. Use section/page-range expansion around high-value hits: p. 1 hit should expand through pp. 2–4; p. 15 hit should expand back to pp. 10–15.
4. Add a generation template for essay mode: thesis + grouped paragraphs for priests/prophets/warriors/kings/gods + citations after each paragraph.
5. Add an answer-completeness check that rejects evidence-only output when the prompt asks for a 500-word answer.

## Q18. Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?

**Test set:** F — Essay-style RAG stress tests

### Expected

- Expected evidence: pp. 1–10
- Good answer should mention: He is king/commander, but rejects Chryses harshly, attacks Kalchas, demands compensation, and takes Briseis.
- Failure signs: Gives a one-sided answer with no evidence for rank/authority.

### Investigator response

```md
Question: Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?
Response: Best evidence:
- [p. 8] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achi...
- [p. 1] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delica...
- [p. 3] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the...
Evidence:
- [p. 8 | p0008_c01] Even 280 though you are the stronger man, and the mother who bore you was immortal, yet is this man greater who is lord over more than you rule: Son of Atreus, give up your anger; even I entreat you to give over your bitterness against Achilleus, he who stands as a great bulwark of battle over all the Achaians.' Then in answer again spoke powerful Agamemnon: 285 'Yes, old sir, all this you have said is fair and orderly.
- [p. 1 | p0001_c01] ONE BOOK S ING, goddess, the anger of Peleus' son Achilleus and its devastation, which put pains thousandfold upon the Achaians, hurled in their multitudes to the house of Hades strong souls of heroes, but gave their bodies to be the delicate feasting of dogs, of all birds, and the will of Zeus was accomplished 5 since that time when first there stood in division of conflict Atreus' son the lord of men and brilliant Achilleus.
- [p. 3 | p0003_c01] 85 In the name of Apollo beloved of Zeus to whom you, Kalchas, make your prayers when you interpret the gods' will to the Danaans, no man so long as I am alive above earth and see daylight shall lay the weight of his hands on you beside the hollow ships, not one of all the Danaans, even if you mean Agamemnon, 90 who now claims to be far the greatest of all the Achaians.' At this the blameless seer took courage again and spoke forth: 'No, it is not for the sake of some vow or hecatomb he blames u...
```

### Subagent evaluation

## Question

“Write a 500-word answer: Is Agamemnon’s authority portrayed as legitimate, abusive, or both in Book 1?”

## Overall finding

The result is **not an acceptable answer**. It returns three evidence snippets rather than a 500-word interpretive response, and it is heavily skewed toward the **legitimacy/rank** side of Agamemnon’s authority. The retrieved citations are within the expected page range (pp. 1–10) and are mostly accurate, but they do not supply the key abusive-authority evidence: Agamemnon’s harsh rejection of Chryses (p. 2), attack on Kalchas and demand for compensation (p. 4), threat to seize Briseis (p. 6), and actual order/removal of Briseis (pp. 9–10).

## Lightweight checks

- **Balanced authority analysis:** Fails. Evidence supports Agamemnon’s status as “lord of men,” “great kingship,” and “sceptred king,” but the answer does not analyze how this authority is abused.
- **Evidence pages 1–10:** Pass. All cited pages are in range: pp. 1, 3, 8.
- **Citations support claims:** Partially. The citations support legitimate/ranked authority, and p. 1/p. 3 gesture toward the crisis caused by dishonoring Chryses. They do not support a balanced “both legitimate and abusive” answer because the strongest abuse passages are absent.

## Rubric scores


| Criterion           | Score | Notes                                                                                                                                                              |
| ------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| retrieval_relevance | 3/5   | Relevant to authority/legitimacy, but misses central abuse passages on pp. 2, 4, 6, 9–10.                                                                          |
| citation_accuracy   | 4/5   | Quoted snippets are generally accurate and correctly paged, though truncated and not integrated.                                                                   |
| speaker_attribution | 2/5   | Snippets preserve some context, but the response does not explain that Nestor, Kalchas, Achilles, etc. are speaking.                                               |
| causal_chain        | 1/5   | Does not explain the chain: Chryses dishonored → Apollo’s plague → Kalchas’ warning → Agamemnon’s anger/compensation demand → Briseis seized → Achilles withdraws. |
| no_hallucination    | 5/5   | No invented claims; problem is omission and lack of synthesis.                                                                                                     |
| answer_quality      | 1/5   | Not a 500-word essay and does not answer “legitimate, abusive, or both” in prose.                                                                                  |


## Diagnosis

- **Retrieval:** Retrieved authority/rank evidence but under-retrieved abuse evidence. It should have included p. 2 (harsh order to Chryses), p. 4 (raging at Kalchas, compensation demand), p. 6 (threat to take Briseis), and pp. 9–10 (execution of threat).
- **Reranking:** Likely overfavored lexical matches for “authority,” “king,” “lord,” and “greater,” causing p. 8/p. 3 to dominate while more causally important conflict passages were omitted.
- **Generation:** Main failure. The model produced an evidence list instead of the requested 500-word answer and did not synthesize a balanced thesis.
- **OCR:** Minor OCR errors exist (e.g., line-number confusions, “takc/hcrc”), but they do not explain this failure.
- **Prompting:** The prompt or answer template may be too evidence-first and insufficiently enforced for essay-style questions.

## Suggested improvements

1. For essay questions, force a prose answer with a thesis before evidence bullets.
2. Add a balance requirement when the question asks “legitimate, abusive, or both”: retrieve and cite at least one passage for each side.
3. Improve reranking with event coverage: Chryses rejection, Kalchas confrontation, compensation demand, Briseis seizure.
4. Add a generation check that rejects evidence-only outputs when the user asks for a 500-word answer.

