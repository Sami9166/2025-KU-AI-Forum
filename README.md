# RAG(Retrieval-Augmented Generation)을 활용한 AI 기반 헤드헌팅 서비스 개발

## Index
[1. Abstact](#Abstract)  
[2. Introduction](#Introduction)  
[3. Method](#Method)  
[4. Result](#Result)  
[5. Conclusion & Future work](#Conclusion-&-Future-work)
[6. References](#References)

## Abstract
본 연구는 중장년층 재취업 과정에서 발생하는 구직자-기업 간 미스매칭 문제를 해결하기 위해 AI 기반 헤드헌팅 서비스를 구현하였다. 한국고용정보원 고령화연구패널(KLoSA) 5~9차 데이터를 활용하여 재취업 이후 직무 만족도에 영향을 미치는 변수를 도출하고, 트리 계열 Classifier와 SHAP 분석을 통해 32개 요인을 선정하여 구직자 매칭 데이터셋을 구성하였다. 구인구직 플랫폼에서 수집한 Job Description을 활용했으며, RAG(Retrieval Augmented Generation)를 적용하여 문맥 기반 의미 유사도와 만족도 요인을 반영한 인재 추천 시스템을 설계하였다. 실제 Job Description을 대상으로 테스트한 결과, 대부분 적합한 인재 추천이 가능하였다. 본 연구는 단순 경력 매칭을 넘어 중장년층 직무 만족도까지 고려한 맞춤형 재취업 추천 방안을 제시했다는 점에서 의의가 있으며, 향후 고용 정책 및 산업 전반의 채용 도구로 확장될 가능성을 보여준다.

## Introduction
중장년층은 퇴직 후에도 경제활동 지속을 희망하지만, 낮은 제도 인지율과 열악한 근로조건으로 미스매칭 문제가 심각하다. 기업은 인바운드 채용 구조와 비효율적인 절차로 인재 확보에 어려움을 겪고 있다. 이를 해결하기 위해 AI 기반 헤드헌팅 서비스 프로토타입을 개발한다. KLoSA 데이터와 실제 채용 공고를 활용해 직무 만족도 요인 분석 및 인재 추천 로직을 설계한다.

## Method
본 연구는 고령화연구패널(KLoSA) 5~9차 데이터를 활용해 이직 경험 후 임금근로자로 재취업한 중장년층 1,340명을 분석 대상으로 선정하고, 결측률, 빈도수,변수 간 연관성을 고려해 42개의 유의미한 변수를 선별하였다. 만족도 5개 문항을 활용해 재취업 직무 만족도 지표를 정의(2.5 기준 ‘높음’, ‘낮음’)하여 분석 모델의 종속변수로 활용하였다. 

클래스 가중치 보정, 계층적 데이터 분할, SMOTE 증강 기법을 적용한 여러 모델 중 트리 계열 Classifier를 활용하여 중장년층 재취업 직무 만족도를 예측하였다. 또한 SHAP을 활용해 변수 중요도와 변수 간 상호작용을 분석하여 총 32개 변수를 최종 요인으로 선정하였다.

직무 만족도가 ‘높음’으로 예측된 데이터만 추출해 수집·정제된 Job Description과 결합하여 RAG 시스템을 구축하였다. Job Description에 명시된 나이, 성별, 근무지역 등을 기본 요건으로 1차 필터링을 거친 뒤 KURE-v1 임베딩 모델로 벡터화하였다. 이후 FAISS를 통해 유사도가 높은 상위 5개를 추출하고, gemma-3n-E4B-it 모델을 Generator로 사용해 최종 3개의 후보군을 선정하도록 설계하였다.

## Result
<img width="1527" height="522" alt="image" src="https://github.com/user-attachments/assets/41911f3a-c1cf-4bed-92db-43a0039dfe42" /> < Confusion Matrix by models >

<img width="1523" height="645" alt="image" src="https://github.com/user-attachments/assets/3555cb1c-9cbc-4262-b9f2-ac96aa8edb72" /> < Top 5 SHAP value >

<img width="1530" height="902" alt="image" src="https://github.com/user-attachments/assets/dd70ab23-7fac-4975-9c27-6018bdead66c" /> < Prototype Example >

## Conclusion & Future work
본 연구는 KLoSA 데이터를 활용하여 이직 만족도에 기여하는 핵심 요인을 도출하고, 이를 Job Description과 RAG 기반 아키텍쳐에 결합해 이직 만족도 중심의 매칭 구조를 구현하였다. 이 과정에서 정보 접근성이 낮은 중장년층을 대상으로 기업 맞춤형 매칭이 실질적 채용 도구로서 작용할 수 있는 가능성을 보여주었다. 다만, 데이터가 한정되어 있어 해당 결과를 일반화하기에는 제약이 존재하므로, 보다 확장된 데이터를 사용하여 요인을 도출할 필요가 있다. 또한, 여러 LLM 모델과 Job Decsription을 대상으로 정량적인 성능 검증이 이루어지지 않아, 향후 이를 체계적으로 평가하고 개선할 필요가 있다.

## References
[1] 김지영, & 이민영. (2022). 중고령 임금근로자의 일자리 특성이 일과 삶의 만족에 미치는 영향: 주관적 계층의식 매개효과를 중심으로. 직업능력개발연구, 25(3), 127–155.

[2]  Patrick Lewis, Ethan Perez (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. https://arxiv.org/abs/2005.11401

[3] Yunfan Gao, Yun Xiong (2023) Retrieval-Augmented Generation for Large Language Models: A Survey. https://arxiv.org/abs/2312.10997
