---
name: tech-debt-audit
description: 프로젝트 코드베이스의 기술 부채(Technical Debt), 코드 악취(Code Smells), 구조적 복잡도를 심층 진단하고 우선순위별 개선 가이드를 제공하는 스킬. 사용 키워드: tech-debt-audit, 기술 부채 진단, 코드 품질 점검, 리팩토링 점검.
---

# TECH-DEBT-AUDIT — 기술 부채 및 코드 품질 진단 스킬

## 개요
코드베이스 전반의 복잡도, 과도한 결합, 중복 로직, 문서화 부재, 테스트 부재 등 기술 부채 요소를 체계적으로 진단하여 안전한 개선 방향을 제시합니다.

## 주요 진단 항목

1. **복잡도 및 코드 악취 (Complexity & Code Smells)**
   - 지나치게 긴 함수/클래스, 깊은 중첩 구조
   - 매직 넘버/스트링의 하드코딩

2. **모듈 결합도 및 응집도 (Coupling & Cohesion)**
   - 강한 결합(Tight coupling) 및 렌더링/비즈니스 로직의 혼재
   - 순환 참조(Circular Dependencies) 가능성

3. **에러 처리 및 예외 안전성 (Error Handling)**
   - 무시되는 예외(Silent Exception suppression)
   - 모호한 에러 메시지 및 자원 해제 누락

4. **가독성 및 유지보수성 (Readability & Maintainability)**
   - 구시대적 구문(Deprecated APIs) 사용
   - 주석과 실제 코드 동작 간의 불일치

## 출력 가이드
- 진단 결과를 **[우선순위 High / Medium / Low]**로 분류하여 제공합니다.
- 각 문제점에 대해 대상 파일, 발생 원인, 권장 리팩토링 방안(Diff 형태 또는 가이드)을 명시합니다.
