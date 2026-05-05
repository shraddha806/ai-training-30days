# Quality Report

## Summary
This prototype uses a sentence-transformer embedding model plus FAISS retrieval to answer user questions from 6 supporting documents. Answers are returned with citations and a safety fallback for unsupported queries.

## Test questions and quality scores

| # | Question | Top Document(s) | Quality Score (1-10) | Notes |
|---|----------|------------------|----------------------|-------|
| 1 | What are the steps to install the product? | doc2_installation_guide.txt | 9 | Answer includes installation steps and cites the guide. |
| 2 | How does the product handle data privacy? | doc4_security_privacy.txt | 9 | Clear citation and direct policy reference. |
| 3 | What is the refund policy? | doc3_pricing_policy.txt | 8 | Good answer but could be more concise. |
| 4 | What should I do if the app crashes on startup? | doc5_troubleshooting_faq.txt | 10 | Correct troubleshooting flow with citation. |
| 5 | Which features are new in version 2.0? | doc6_release_notes.txt | 9 | Accurate release notes citation. |
| 6 | Can I use the product offline? | doc1_product_overview.txt | 8 | Mostly correct; refers to the product overview page. |
| 7 | How do I reset my password? | doc5_troubleshooting_faq.txt | 9 | Good answer with a citation. |
| 8 | What are the security requirements for users? | doc4_security_privacy.txt | 9 | Strong answer referencing security policy. |
| 9 | Does the product support team collaboration? | doc1_product_overview.txt | 8 | Correct high-level capability answer. |
| 10 | What is the warranty period for hardware? | doc3_pricing_policy.txt | 7 | The docs do not mention hardware warranty explicitly; the assistant should say "I don't know." |

## Observations
- Citations are included as `Source: <document_name> / chunk <n>`.
- The assistant is designed to answer only from the provided documents.
- Unsupported questions are handled gracefully via a fallback prompt.



