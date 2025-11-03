#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config

# Configurações do MinIO
MINIO_SERVER_URL = "https://c4crm-minio.zv7gpn.easypanel.host"
MINIO_ROOT_USER = "admin"
MINIO_ROOT_PASSWORD = "Devs@0101"

print("🔍 Testando acesso ao MinIO via boto3...")

try:
    # Configurar cliente S3 para MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url=MINIO_SERVER_URL,
        aws_access_key_id=MINIO_ROOT_USER,
        aws_secret_access_key=MINIO_ROOT_PASSWORD,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'  # MinIO geralmente usa us-east-1 como padrão
    )
    
    print("✅ Cliente S3 criado com sucesso!")
    
    # Listar buckets
    print("\n📦 Listando buckets...")
    try:
        response = s3_client.list_buckets()
        buckets = response.get('Buckets', [])
        
        if buckets:
            print(f"✅ Encontrados {len(buckets)} buckets:")
            for bucket in buckets:
                print(f"   📁 {bucket['Name']} (criado em {bucket['CreationDate']})")
        else:
            print("❌ Nenhum bucket encontrado")
            
    except ClientError as e:
        print(f"❌ Erro ao listar buckets: {e}")
    
    # Tentar acessar bucket 'produtos' se existir
    print("\n🎯 Testando acesso ao bucket 'produtos'...")
    try:
        response = s3_client.list_objects_v2(Bucket='produtos', MaxKeys=10)
        objects = response.get('Contents', [])
        
        if objects:
            print(f"✅ Encontrados {len(objects)} objetos no bucket 'produtos':")
            for obj in objects[:5]:  # Mostrar apenas os primeiros 5
                print(f"   📄 {obj['Key']} ({obj['Size']} bytes)")
                
                # Se encontrar um arquivo de banner, tentar gerar URL
                if 'banner' in obj['Key'].lower():
                    print(f"   🎯 Arquivo de banner encontrado: {obj['Key']}")
                    
                    # Gerar URL pré-assinada
                    try:
                        url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': 'produtos', 'Key': obj['Key']},
                            ExpiresIn=3600  # 1 hora
                        )
                        print(f"   🔗 URL pré-assinada: {url[:100]}...")
                    except Exception as e:
                        print(f"   ❌ Erro ao gerar URL: {e}")
        else:
            print("❌ Nenhum objeto encontrado no bucket 'produtos'")
            
    except ClientError as e:
        print(f"❌ Erro ao acessar bucket 'produtos': {e}")
        
        # Tentar outros buckets comuns
        common_buckets = ['images', 'assets', 'uploads', 'files', 'media']
        for bucket_name in common_buckets:
            try:
                print(f"\n🔍 Testando bucket '{bucket_name}'...")
                response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
                objects = response.get('Contents', [])
                if objects:
                    print(f"✅ Bucket '{bucket_name}' existe com {len(objects)} objetos")
                    for obj in objects:
                        print(f"   📄 {obj['Key']}")
                    break
            except ClientError:
                continue
    
except NoCredentialsError:
    print("❌ Credenciais não configuradas")
except Exception as e:
    print(f"❌ Erro geral: {e}")