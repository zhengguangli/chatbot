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

@pytest.mark.anyio
class TestEndToEnd:
    """端到端测试类"""

    adapter: UIAdapter
    service_container: ServiceContainer
    test_results: Dict[str, bool]

    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """设置和清理测试环境"""
        print("🔧 设置测试环境...")
        self.test_results = {}
        
        # 创建服务容器
        self.service_container = ServiceContainer()
        await self.service_container.initialize()
        
        # 创建UI适配器
        self.adapter = UIAdapter()
        await self.adapter.initialize()
        
        print("✅ 测试环境设置完成")
        
        yield # 这里是测试执行的地方
        
        print("🧹 清理测试环境...")
        if self.adapter:
            await self.adapter.close()
        
        if self.service_container:
            await self.service_container.close()
            
        print("✅ 测试环境清理完成")

        self.print_test_summary()

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
            pytest.fail(f"服务容器生命周期测试失败: {e}")
            
    async def test_session_management_flow(self):
        """测试会话管理流程"""
        print("\n💬 测试会话管理流程...")
        
        try:
            session_manager = self.service_container.get_service('session_manager')
            assert session_manager is not None

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
                "user",
                test_message
            )
            assert message is not None, "应该成功添加消息"
            assert message.content == test_message, "消息内容应该匹配"
            
            # 获取会话历史
            history = await session_manager.get_session_messages(session.session_id)
            assert len(history) >= 1, "历史记录应该包含至少1条消息"
            assert history[0].content == test_message, "历史消息内容应该匹配"
            
            # 获取用户会话列表
            user_sessions = await session_manager.get_user_sessions(test_user_id)
            assert len(user_sessions) >= 1, "用户应该至少有一个会话"
            
            self.test_results['session_management_flow'] = True
            print("✅ 会话管理流程测试通过")
            
        except Exception as e:
            self.test_results['session_management_flow'] = False
            print(f"❌ 会话管理流程测试失败: {e}")
            pytest.fail(f"会话管理流程测试失败: {e}")
            
    async def test_message_processing_flow(self):
        """测试消息处理流程"""
        from src.contracts.message_handler import MessageContext

        print("\n📝 测试消息处理流程...")
        
        try:
            message_handler = self.service_container.get_service('message_handler')
            assert message_handler is not None

            context = MessageContext(session_id="test", user_id="test", conversation_history=[], system_settings={}, user_preferences={})

            test_inputs = [
                "普通消息测试",
                "带有特殊字符的消息：!@#$%^&*()",
                "多行消息\n第二行\n第三行",
                "/help 命令测试",
                "很长的消息" + "内容" * 100
            ]
            
            for test_input in test_inputs:
                processed = await message_handler.process_user_message(test_input, context)
                assert processed is not None and processed.is_valid, f"消息处理应该成功: {test_input[:50]}..."
                
            self.test_results['message_processing_flow'] = True
            print("✅ 消息处理流程测试通过")
            
        except Exception as e:
            self.test_results['message_processing_flow'] = False
            print(f"❌ 消息处理流程测试失败: {e}")
            pytest.fail(f"消息处理流程测试失败: {e}")
            
    async def test_model_provider_flow(self):
        """测试模型提供者流程"""
        from src.contracts.model_provider import ModelConfig
        print("\n🤖 测试模型提供者流程...")
        
        try:
            model_registry = self.service_container.get_service('model_registry')
            assert model_registry is not None
            
            default_provider = model_registry.get_provider()
            assert default_provider is not None, "应该有默认模型提供者"
            
            test_messages = [{"role": "user", "content": "这是一个测试提示"}]
            config = ModelConfig(model_name="qwen3", provider="openai")
            response = await default_provider.generate_response(test_messages, config)
            assert response is not None, "应该生成响应"
            assert hasattr(response, 'content'), "响应应该有内容属性"
            
            is_valid_config = await default_provider.validate_config(config)
            assert is_valid_config, "配置应该有效"
            
            self.test_results['model_provider_flow'] = True
            print("✅ 模型提供者流程测试通过")
            
        except Exception as e:
            self.test_results['model_provider_flow'] = False
            print(f"❌ 模型提供者流程测试失败: {e}")
            pytest.fail(f"模型提供者流程测试失败: {e}")
            
    async def test_storage_persistence_flow(self):
        """测试存储持久化流程"""
        print("\n💾 测试存储持久化流程...")
        
        try:
            storage_service = self.service_container.get_service('storage_service')
            assert storage_service is not None
            
            test_collection = "test_data"
            test_id = "test_001"
            test_data = {
                "name": "测试数据",
                "timestamp": time.time(),
                "metadata": {"test": True}
            }
            
            await storage_service.store_data(test_collection, test_data, test_id)
            
            retrieved = await storage_service.retrieve_data(test_collection, test_id)
            assert retrieved is not None, "应该能检索到数据"
            assert retrieved["name"] == test_data["name"], "检索的数据应该匹配"
            
            from src.contracts.storage_service import QueryOptions
            query_results = await storage_service.query_data(test_collection, QueryOptions(filters=[]))
            assert len(query_results) >= 1, "查询应该返回结果"
            
            deleted = await storage_service.delete_data(test_collection, test_id)
            assert deleted, "数据删除应该成功"
            
            self.test_results['storage_persistence_flow'] = True
            print("✅ 存储持久化流程测试通过")
            
        except Exception as e:
            self.test_results['storage_persistence_flow'] = False
            print(f"❌ 存储持久化流程测试失败: {e}")
            pytest.fail(f"存储持久化流程测试失败: {e}")

    async def test_ui_compatibility_flow(self):
        """测试UI兼容性流程"""
        print("\n🖥️ 测试UI兼容性流程...")
        
        try:
            # 测试兼容性函数
            client = await initialize_openai_client()
            assert client is not None, "应该成功初始化客户端"
            
            # 测试聊天响应
            test_message = "测试兼容性接口"
            response = await get_chatbot_response(client, test_message, [])
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
            pytest.fail(f"UI兼容性流程测试失败: {e}")

    async def test_full_user_conversation_flow(self):
        """测试完整用户对话流程"""
        print("\n💭 测试完整用户对话流程...")
        
        try:
            test_user_id = "e2e_test_user"
            conversation_history = []
            
            session_manager = self.service_container.get_service('session_manager')
            assert session_manager is not None
            session = await session_manager.create_session(test_user_id)
            
            test_messages = [
                "你好！我想了解一下这个聊天机器人",
                "它有什么功能？",
            ]
            
            for i, user_message in enumerate(test_messages):
                conversation_history.append({"role": "user", "content": user_message})
                
                ai_response = await self.adapter.get_chatbot_response(
                    user_message, 
                    conversation_history
                )
                
                conversation_history.append({"role": "assistant", "content": ai_response})
                
                print(f"  轮次 {i+1}: 用户消息和AI响应成功")
            
            # The test was failing because add_message wasn't called.
            # However, get_chatbot_response already calls add_message internally.
            # So we just need to verify the history.
            
            messages = await session_manager.get_session_messages(session.session_id)
            assert len(messages) >= len(test_messages) * 2, "历史记录应该包含所有消息"
            
            self.test_results['full_user_conversation_flow'] = True
            print("✅ 完整用户对话流程测试通过")
            
        except Exception as e:
            self.test_results['full_user_conversation_flow'] = False
            print(f"❌ 完整用户对话流程测试失败: {e}")
            pytest.fail(f"完整用户对话流程测试失败: {e}")

    def print_test_summary(self):
        """打印测试总结"""
        if not self.test_results:
            return

        print("\n" + "="*60)
        print("🎯 端到端测试总结")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数量: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        
        if total_tests > 0:
            print(f"通过率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in self.test_results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {test_name}: {status}")
            
        print("\n" + "="*60)
        
        if failed_tests == 0 and total_tests > 0:
            print("🎉 所有端到端测试通过！架构重构验证成功！")
        elif total_tests > 0:
            print(f"⚠️  有 {failed_tests} 个测试失败，需要进一步检查")

# This allows running the test file directly for debugging
if __name__ == "__main__":
    async def run():
        test = TestEndToEnd()
        await test.setup_and_teardown.__wrapped__(test) # type: ignore
        await test.test_service_container_lifecycle()
        await test.test_session_management_flow()
        await test.test_message_processing_flow()
        await test.test_model_provider_flow()
        await test.test_storage_persistence_flow()
        await test.test_ui_compatibility_flow()
        await test.test_full_user_conversation_flow()
        test.print_test_summary()
        await test.setup_and_teardown.__wrapped__(test).gen.aclose() # type: ignore

    asyncio.run(run()) 