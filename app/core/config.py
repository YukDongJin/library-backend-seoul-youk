# 📁 새로 생성된 파일: app/core/config.py
# 애플리케이션 설정 관리

from pydantic_settings import BaseSettings
from typing import List, Optional, Dict, Any
import os
import boto3
import json


def get_db_secrets_from_aws(secret_name: str, region: str = "ap-northeast-2") -> Dict[str, Any]:
    """AWS Secrets Manager에서 DB 정보 전체 가져오기"""
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret = response.get("SecretString", "")
        # JSON 형식 파싱
        secret_dict = json.loads(secret)
        print(f"✅ Secrets Manager에서 DB 정보 로드 완료: {secret_name}")
        return secret_dict
    except Exception as e:
        print(f"⚠️ Secrets Manager 호출 실패: {e}")
        return {}


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    - 환경 변수를 자동으로 로드
    - 타입 검증 및 기본값 설정
    - 개발/운영 환경 분리
    """
    
    # 서버 설정
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 데이터베이스 설정 (Secrets Manager에서 로드됨)
    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    
    # AWS Secrets Manager 설정
    USE_SECRETS_MANAGER: bool = True
    DB_SECRET_NAME: str = "database"  # 시크릿 이름
    
    # AWS Cognito 설정
    AWS_REGION: str = "ap-northeast-2"
    COGNITO_USER_POOL_ID: str = "ap-northeast-2_mFvtIc1kQ"
    COGNITO_CLIENT_ID: str = "3c0kds3554rvakp9piqv694at2"
    
    # AWS S3 설정 (IRSA 사용 - Access Key 불필요)
    S3_BUCKET_NAME: str = "knowledge-base-test-6575574"
    S3_REGION: str = "ap-northeast-2"
    
    # AWS Step Functions 설정 (동영상 프리뷰 생성용)
    VIDEO_PREVIEW_STATE_MACHINE_ARN: str = ""
    
    # AWS Step Functions 설정 (AI 제목 생성용)
    AI_TITLE_GENERATOR_STATE_MACHINE_ARN: str = ""
    
    # 내부 서비스 API 키 (Lambda에서 백엔드 호출 시 사용)
    INTERNAL_API_KEY: str = "fproject-internal-service-key-2024"
    
    # 백엔드 기본 URL (파일 프록시용)
    BACKEND_BASE_URL: str = "https://api.aws11.shop"
    
    # JWT 설정
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 프로젝트 정보
    PROJECT_NAME: str = "Library Management API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend for library management system"
    
    class Config:
        # .env 파일에서 환경 변수 로드
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def database_url_sync(self) -> str:
        """동기 데이터베이스 URL (Alembic 마이그레이션용)"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_url_async(self) -> str:
        """비동기 데이터베이스 URL (FastAPI용)"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# 전역 설정 인스턴스
settings = Settings()

# Secrets Manager에서 DB 정보 전체 가져오기
if settings.USE_SECRETS_MANAGER:
    print("🔐 AWS Secrets Manager에서 DB 정보 가져오는 중...")
    db_secrets = get_db_secrets_from_aws(
        settings.DB_SECRET_NAME, 
        settings.AWS_REGION
    )
    if db_secrets:
        # 시크릿에서 DB 정보 설정 (환경변수보다 우선)
        settings.DB_HOST = db_secrets.get("host", settings.DB_HOST)
        settings.DB_PORT = int(db_secrets.get("port", settings.DB_PORT))
        settings.DB_NAME = db_secrets.get("dbname", settings.DB_NAME)
        settings.DB_USER = db_secrets.get("username", settings.DB_USER)  # Secret Manager 키: username
        settings.DB_PASSWORD = db_secrets.get("password", settings.DB_PASSWORD)
        print("✅ DB 정보 로드 완료")
    else:
        print("⚠️ Secrets Manager에서 DB 정보를 가져오지 못했습니다. 환경변수 사용.")

# 개발 환경에서만 설정 정보 출력
if settings.DEBUG:
    print("🔧 애플리케이션 설정 로드 완료")
    print(f"📊 데이터베이스: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")
    print(f"👤 DB 사용자: {settings.DB_USER}")
    print(f"🌐 서버: {settings.HOST}:{settings.PORT}")
    print(f"🔐 JWT 알고리즘: {settings.JWT_ALGORITHM}")
    print(f"☁️ AWS 리전: {settings.AWS_REGION}")
    print(f"🪣 S3 버킷: {settings.S3_BUCKET_NAME}")
