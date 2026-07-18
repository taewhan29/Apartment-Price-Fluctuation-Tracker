---
name: security-research
description: 코드베이스의 보안 취약점(취약한 패키지, 하드코딩된 시크릿, 오염된 입력값 처리, SQLi/XSS/Command Injection 등)을 진단하고 조치 방안을 제시하는 보안 스킬. 사용 키워드: security-research, 보안 점검, 취약점 진단, 시크릿 점검.
---

# SECURITY-RESEARCH — 보안 취약점 감사 스킬

## 개요
애플리케이션 및 소스코드 보안 취약점을 사전에 진단하고, 하드코딩된 자격 증명, 입력값 검증 누락, 보안 취약 패키지 사용 등을 탐지하여 조치 방안을 제시합니다.

## 핵심 점검 항목

1. **하드코딩된 시크릿 (Hardcoded Secrets)**
   - API 키, 비밀번호, 토큰, 프라이빗 키의 소스코드 내 하드코딩 여부 점검

2. **입력값 검증 및 인젝션 (Input Validation & Injection)**
   - 사용자 입력값이 Sanitization 없이 쿼리/명령어/스크립트에 전달되는지 점검

3. **권한 및 인증 (Auth & Access Control)**
   - 민감 데이터 노출 및 적절하지 않은 이스케이프 처리 확인

4. **의존성 패키지 안전성 (Dependency Security)**
   - 알려진 취약점이 있는 패키지 버전 사용 여부 확인

## 결과 리포트
- 취약점의 심각도(Critical / High / Medium / Low) 명시
- 영향받는 코드 위치(`file://...`) 및 구체적인 패치를 위한 보안 권고안 제시
