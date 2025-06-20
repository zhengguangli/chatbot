"""
端到端测试套件
测试完整的用户流程，确保重构后的架构功能完整性
"""

import asyncio
import pytest
import sys
import os
import time
from typing import Dict, Any, List

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ui.adapters import UIAdapter
from src.ui.compatibility import initialize_openai_client, get_chatbot_response
from src.services.service_container import ServiceContainer


class TestEndToEnd:
    """端到端测试类"""
    
    def __init__(self):
        self.adapter = None
        self.service_container = None
        self.test_results = {}
        
    async def setup_test_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建服务容器
        self.service_container = ServiceContainer()
        await self.service_container.initialize()
        
        # 创建UI适配器
        self.adapter = UIAdapter()
        await self.adapter.initialize()
        
        print("✅ 测试环境设置完成")
        
    async def cleanup_test_environment(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")
        
        if self.adapter:
            await self.adapter.close()
        
        if self.service_container:
            await self.service_container.close()
            
        print("✅ 测试环境清理完成")
        
    async def test_service_container_lifecycle(self):
        """测试服务容器生命周期"""
        print("\n📦 测试服务容器生命周期...")
        
        try:
            # 测试服务初始化
            assert self.service_container.is_initialized(), "服务容器应该已初始化"
            
            # 测试服务获取
            storage_service = self.service_container.get_service('storage_service')
            session_manager = self.service_container.get_service('session_manager')
            message_handler = self.service_container.get_service('message_handler')
            
            assert storage_service is not None, "存储服务应该可用"
            assert session_manager is not None, "会话管理器应该可用"
            assert message_handler is not None, "消息处理器应该可用"
            
            self.test_results['service_container_lifecycle'] = True
            print("✅ 服务容器生命周期测试通过")
            
        except Exception as e:
            self.test_results['service_container_lifecycle'] = False
            print(f"❌ 服务容器生命周期测试失败: {e}")
            
    async def test_session_management_flow(self):
        """测试会话管理流程"""
        print("\n💬 测试会话管理流程...")
        
        try:
            session_manager = self.service_container.get_service('session_manager')
            
            # 创建测试用户
            test_user_id = "test_user_001"
            
            # 创建新会话
            session = await session_manager.create_session(test_user_id)
            assert session is not None, "应该成功创建会话"
            assert session.user_id == test_user_id, "会话用户ID应该匹配"
            
            # 添加消息
            test_message = "你好，这是一条测试消息"
            message = await session_manager.add_message(
                session.session_id, 
                test_message, 
                "user"
            )
            assert message is not None, "应该成功添加消息"
            assert message.content == test_message, "消息内容应该匹配"
            
            # 获取会话历史
            history = await session_manager.get_session_history(session.session_id)
            assert len(history) == 1, "历史记录应该包含1条消息"
            assert history[0].content == test_message, "历史消息内容应该匹配"
            
            # 获取用户会话列表
            user_sessions = await session_manager.get_user_sessions(test_user_id)
            assert len(user_sessions) >= 1, "用户应该至少有一个会话"
            
            self.test_results['session_management_flow'] = True
            print("✅ 会话管理流程测试通过")
            
        except Exception as e:
            self.test_results['session_management_flow'] = False
            print(f"❌ 会话管理流程测试失败: {e}")
            
    async def test_message_processing_flow(self):
        """测试消息处理流程"""
        print("\n📝 测试消息处理流程...")
        
        try:
            message_handler = self.service_container.get_service('message_handler')
            
            # 测试输入验证
            test_inputs = [
                "普通消息测试",
                "带有特殊字符的消息：!@#$%^&*()",
                "多行消息\n第二行\n第三行",
                "/help 命令测试",
                "很长的消息" + "内容" * 100
            ]
            
            for test_input in test_inputs:
                # 验证输入
                is_valid = await message_handler.validate_input(test_input)
                assert is_valid, f"输入应该有效: {test_input[:50]}..."
                
                # 处理消息
                processed = await message_handler.process_message(test_input, {})
                assert processed is not None, "消息处理应该成功"
                
            self.test_results['message_processing_flow'] = True
            print("✅ 消息处理流程测试通过")
            
        except Exception as e:
            self.test_results['message_processing_flow'] = False
            print(f"❌ 消息处理流程测试失败: {e}")
            
    async def test_model_provider_flow(self):
        """测试模型提供者流程"""
        print("\n🤖 测试模型提供者流程...")
        
        try:
            model_registry = self.service_container.get_service('model_registry')
            
            # 获取默认提供者
            default_provider = model_registry.get_default_provider()
            assert default_provider is not None, "应该有默认模型提供者"
            
            # 测试模型响应生成
            test_prompt = "这是一个测试提示"
            response = await default_provider.generate_response(test_prompt)
            assert response is not None, "应该生成响应"
            assert hasattr(response, 'content'), "响应应该有内容属性"
            
            # 测试配置验证
            config = default_provider.get_current_config()
            assert config is not None, "应该有当前配置"
            
            self.test_results['model_provider_flow'] = True
            print("✅ 模型提供者流程测试通过")
            
        except Exception as e:
            self.test_results['model_provider_flow'] = False
            print(f"❌ 模型提供者流程测试失败: {e}")
            
    async def test_storage_persistence_flow(self):
        """测试存储持久化流程"""
        print("\n💾 测试存储持久化流程...")
        
        try:
            storage_service = self.service_container.get_service('storage_service')
            
            # 测试数据存储和检索
            test_collection = "test_data"
            test_data = {
                "id": "test_001",
                "name": "测试数据",
                "timestamp": time.time(),
                "metadata": {"test": True}
            }
            
            # 存储数据
            result = await storage_service.store(test_collection, test_data["id"], test_data)
            assert result, "数据存储应该成功"
            
            # 检索数据
            retrieved = await storage_service.retrieve(test_collection, test_data["id"])
            assert retrieved is not None, "应该能检索到数据"
            assert retrieved["name"] == test_data["name"], "检索的数据应该匹配"
            
            # 查询数据
            query_results = await storage_service.query(test_collection, {"test": True})
            assert len(query_results) >= 1, "查询应该返回结果"
            
            # 删除数据
            deleted = await storage_service.delete(test_collection, test_data["id"])
            assert deleted, "数据删除应该成功"
            
            self.test_results['storage_persistence_flow'] = True
            print("✅ 存储持久化流程测试通过")
            
        except Exception as e:
            self.test_results['storage_persistence_flow'] = False
            print(f"❌ 存储持久化流程测试失败: {e}")
            
    async def test_ui_compatibility_flow(self):
        """测试UI兼容性流程"""
        print("\n🖥️ 测试UI兼容性流程...")
        
        try:
            # 测试兼容性函数
            client = initialize_openai_client()
            assert client is not None, "应该成功初始化客户端"
            
            # 测试聊天响应
            test_message = "测试兼容性接口"
            response = get_chatbot_response(test_message, [])
            assert response is not None, "应该生成响应"
            assert isinstance(response, str), "响应应该是字符串"
            
            # 测试适配器接口
            adapter_response = await self.adapter.get_chatbot_response(test_message, [])
            assert adapter_response is not None, "适配器应该生成响应"
            
            self.test_results['ui_compatibility_flow'] = True
            print("✅ UI兼容性流程测试通过")
            
        except Exception as e:
            self.test_results['ui_compatibility_flow'] = False
            print(f"❌ UI兼容性流程测试失败: {e}")
            
    async def test_error_handling_flow(self):
        """测试错误处理流程"""
        print("\n⚠️ 测试错误处理流程...")
        
        try:
            from src.core.errors import ValidationError, APIError, NetworkError
            
            # 测试验证错误
            try:
                raise ValidationError("测试验证错误", {"field": "test"})
            except ValidationError as e:
                assert "测试验证错误" in str(e), "错误消息应该包含测试文本"
                assert e.context["field"] == "test", "错误上下文应该匹配"
            
            # 测试API错误
            try:
                raise APIError("测试API错误", error_code="TEST_001")
            except APIError as e:
                assert e.error_code == "TEST_001", "错误代码应该匹配"
            
            # 测试网络错误
            try:
                raise NetworkError("测试网络错误", retry_count=3)
            except NetworkError as e:
                assert e.retry_count == 3, "重试次数应该匹配"
            
            self.test_results['error_handling_flow'] = True
            print("✅ 错误处理流程测试通过")
            
        except Exception as e:
            self.test_results['error_handling_flow'] = False
            print(f"❌ 错误处理流程测试失败: {e}")
            
    async def test_full_user_conversation_flow(self):
        """测试完整用户对话流程"""
        print("\n💭 测试完整用户对话流程...")
        
        try:
            # 模拟完整的用户对话
            test_user_id = "e2e_test_user"
            conversation_history = []
            
            # 创建会话
            session_manager = self.service_container.get_service('session_manager')
            session = await session_manager.create_session(test_user_id)
            
            # 模拟多轮对话
            test_messages = [
                "你好！我想了解一下这个聊天机器人",
                "它有什么功能？",
                "我可以问技术问题吗？",
                "谢谢你的回答！"
            ]
            
            for i, user_message in enumerate(test_messages):
                # 添加用户消息
                await session_manager.add_message(
                    session.session_id, 
                    user_message, 
                    "user"
                )
                conversation_history.append({"role": "user", "content": user_message})
                
                # 获取AI响应
                ai_response = await self.adapter.get_chatbot_response(
                    user_message, 
                    conversation_history
                )
                
                # 添加AI消息
                await session_manager.add_message(
                    session.session_id, 
                    ai_response, 
                    "assistant"
                )
                conversation_history.append({"role": "assistant", "content": ai_response})
                
                print(f"  轮次 {i+1}: 用户消息和AI响应成功")
            
            # 验证对话历史
            history = await session_manager.get_session_history(session.session_id)
            assert len(history) == len(test_messages) * 2, "历史记录应该包含所有消息"
            
            self.test_results['full_user_conversation_flow'] = True
            print("✅ 完整用户对话流程测试通过")
            
        except Exception as e:
            self.test_results['full_user_conversation_flow'] = False
            print(f"❌ 完整用户对话流程测试失败: {e}")
            
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("🎯 端到端测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数量: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            
        print("\n" + "="*60)
        
        if failed_tests == 0:
            print("🎉 所有端到端测试通过！架构重构验证成功！")
        else:
            print(f"⚠️  有 {failed_tests} 个测试失败，需要进一步检查")


async def run_end_to_end_tests():
    """运行端到端测试套件"""
    print("🚀 开始端到端测试套件")
    print("="*60)
    
    test_suite = TestEndToEnd()
    
    try:
        # 设置测试环境
        await test_suite.setup_test_environment()
        
        # 运行所有测试
        await test_suite.test_service_container_lifecycle()
        await test_suite.test_session_management_flow()
        await test_suite.test_message_processing_flow()
        await test_suite.test_model_provider_flow()
        await test_suite.test_storage_persistence_flow()
        await test_suite.test_ui_compatibility_flow()
        await test_suite.test_error_handling_flow()
        await test_suite.test_full_user_conversation_flow()
        
        # 打印测试总结
        test_suite.print_test_summary()
        
    finally:
        # 清理测试环境
        await test_suite.cleanup_test_environment()


if __name__ == "__main__":
    asyncio.run(run_end_to_end_tests()) 