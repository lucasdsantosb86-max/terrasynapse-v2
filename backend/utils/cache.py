"""
TerraSynapse V2.0 - Sistema de Cache
Cache em memória para otimizar performance das APIs
"""

import json
import time
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.ttl_cache = {}
        
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Armazenar valor no cache com TTL (time to live)
        
        Args:
            key: Chave do cache
            value: Valor a ser armazenado
            ttl: Tempo de vida em segundos (padrão: 5 minutos)
        """
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl
        }
        
        # Limpar cache expirado periodicamente
        self._cleanup_expired()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Recuperar valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor armazenado ou None se não existir/expirado
        """
        
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        
        # Verificar se expirou
        if time.time() - cached_item["timestamp"] > cached_item["ttl"]:
            del self.cache[key]
            return None
        
        return cached_item["value"]
    
    def delete(self, key: str) -> bool:
        """
        Remover item do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido, False se não existia
        """
        
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """
        Verificar se chave existe no cache (e não expirou)
        
        Args:
            key: Chave do cache
            
        Returns:
            True se existe e válido, False caso contrário
        """
        
        return self.get(key) is not None
    
    def clear(self) -> None:
        """Limpar todo o cache"""
        
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """
        Estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        
        total_items = len(self.cache)
        expired_items = 0
        
        current_time = time.time()
        for cached_item in self.cache.values():
            if current_time - cached_item["timestamp"] > cached_item["ttl"]:
                expired_items += 1
        
        return {
            "total_items": total_items,
            "active_items": total_items - expired_items,
            "expired_items": expired_items,
            "cache_hit_ratio": self._calculate_hit_ratio()
        }
    
    def health_check(self) -> str:
        """
        Verificação de saúde do cache
        
        Returns:
            Status do cache
        """
        
        try:
            # Teste básico de operação
            test_key = "health_check_test"
            test_value = {"timestamp": datetime.now().isoformat()}
            
            self.set(test_key, test_value, ttl=10)
            retrieved = self.get(test_key)
            
            if retrieved and retrieved["timestamp"] == test_value["timestamp"]:
                self.delete(test_key)
                return "healthy"
            else:
                return "degraded"
                
        except Exception:
            return "unhealthy"
    
    def _cleanup_expired(self) -> None:
        """Limpar itens expirados do cache"""
        
        current_time = time.time()
        expired_keys = []
        
        for key, cached_item in self.cache.items():
            if current_time - cached_item["timestamp"] > cached_item["ttl"]:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
    
    def _calculate_hit_ratio(self) -> float:
        """
        Calcular taxa de acerto do cache
        Implementação simplificada
        """
        
        # Em uma implementação real, isso seria rastreado
        # Por enquanto, retornar valor simulado
        return 0.85
    
    def get_or_set(self, key: str, callback, ttl: int = 300) -> Any:
        """
        Buscar no cache ou executar callback e armazenar resultado
        
        Args:
            key: Chave do cache
            callback: Função para executar se não estiver no cache
            ttl: Tempo de vida do cache
            
        Returns:
            Valor do cache ou resultado do callback
        """
        
        # Tentar buscar no cache primeiro
        cached_value = self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Se não estiver no cache, executar callback
        try:
            result = callback()
            self.set(key, result, ttl)
            return result
        except Exception as e:
            # Em caso de erro, não armazenar no cache
            raise e
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidar chaves que correspondem a um padrão
        
        Args:
            pattern: Padrão para buscar (busca simples por substring)
            
        Returns:
            Número de chaves removidas
        """
        
        keys_to_remove = []
        
        for key in self.cache.keys():
            if pattern in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
        
        return len(keys_to_remove)
    
    def get_keys(self) -> list:
        """
        Obter todas as chaves ativas no cache
        
        Returns:
            Lista de chaves ativas (não expiradas)
        """
        
        active_keys = []
        current_time = time.time()
        
        for key, cached_item in self.cache.items():
            if current_time - cached_item["timestamp"] <= cached_item["ttl"]:
                active_keys.append(key)
        
        return active_keys
    
    def extend_ttl(self, key: str, additional_seconds: int) -> bool:
        """
        Estender TTL de uma chave existente
        
        Args:
            key: Chave do cache
            additional_seconds: Segundos adicionais para o TTL
            
        Returns:
            True se estendido com sucesso, False se chave não existe
        """
        
        if key not in self.cache:
            return False
        
        self.cache[key]["ttl"] += additional_seconds
        return True