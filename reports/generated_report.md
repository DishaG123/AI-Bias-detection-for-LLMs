# Independent Study Report: Normativity Audit of LLM Responses

## 1. Project Overview
This project converts manual AI ethics experiments into a reproducible codebase for testing how language models reproduce gender, cultural, safety, class, caste, disability, and appearance norms.

## 2. Method
The codebase uses a hierarchical prompt bank of 100 prompts. Prompts are grouped by domain, subdomain, target group, and expected risk. Each prompt is sent to selected model providers, saved as JSON, and scored using heuristic discourse-analysis detectors.

## 3. Manual Experiments
The manual phase should document screenshots and close readings, including color-career prompts, toy/ambition prompts, India vs US image descriptions, eve-teasing advice, dowry, and marriage/income prompts.

## 4. Scripted Experiments and Results
### safety_audit
Hierarchical prompt audit for the safety domain.
- Responses scored: 10
- Average bias score: 0.136
- High-risk responses (>0.60): 2

### career_audit
Hierarchical prompt audit for the career domain.
- Responses scored: 10
- Average bias score: 0.231
- High-risk responses (>0.60): 2

### culture_audit
Hierarchical prompt audit for the culture domain.
- Responses scored: 10
- Average bias score: 0.456
- High-risk responses (>0.60): 6

### family_audit
Hierarchical prompt audit for the family domain.
- Responses scored: 10
- Average bias score: 0.128
- High-risk responses (>0.60): 2

### appearance_audit
Hierarchical prompt audit for the appearance domain.
- Responses scored: 10
- Average bias score: 0.192
- High-risk responses (>0.60): 3

### identity_audit
Hierarchical prompt audit for the identity domain.
- Responses scored: 10
- Average bias score: 0.128
- High-risk responses (>0.60): 2

### disability_audit
Hierarchical prompt audit for the disability domain.
- Responses scored: 10
- Average bias score: 0.064
- High-risk responses (>0.60): 1

### policy_audit
Hierarchical prompt audit for the policy domain.
- Responses scored: 10
- Average bias score: 0.192
- High-risk responses (>0.60): 3

### general_audit
Hierarchical prompt audit for the general domain.
- Responses scored: 10
- Average bias score: 0.128
- High-risk responses (>0.60): 2

## 5. Aggregate Findings
Overall average bias score: 0.184

### Provider comparison
- mock: average score 0.184 across 90 responses

### Most frequent bias signals
- western_default: 16
- victim_blaming: 4
- gender_stereotype: 4
- cultural_stereotype: 2
- harm_normalization: 1

## 6. Interpretation
The scores are not ground truth. They are a way to organize qualitative reading. The strongest claims should come from comparing paired prompts and then manually interpreting the language differences.

## 7. Limitations
The detectors are lexical and can miss subtle bias. They can also overcount words used critically. Future work should add human annotation, model-judge evaluation, and repeated trials over time.