"""
Scenario Orchestration Service
Coordinates multiple security operations for automated incident response workflows
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .security_incidents_service import SecurityIncidentsService
from .ipblock_service import IpBlockService


class ScenarioOrchestrationService:
    """场景任务编排服务 - 负责协调多个skill完成复杂场景"""

    def __init__(self):
        self.incidents_service = SecurityIncidentsService()

    async def execute_daily_high_risk_closure(
        self,
        auth_code: str,
        base_url: str,
        provider: str = None,
        api_key: str = None,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行每日高危事件闭环场景 (步骤1-3)

        步骤:
        1. 查询今日未处置的高危及严重事件
        2. 分析Top 1事件 (并行获取详情和IP实体)
        3. 准备确认信息

        Args:
            auth_code: Flux认证码
            base_url: Flux API地址
            provider: LLM提供商 (暂不使用,预留扩展)
            api_key: LLM API密钥 (暂不使用,预留扩展)
            llm_base_url: LLM API地址 (暂不使用,预留扩展)

        Returns:
            包含场景执行状态和数据的字典
        """
        # Step 1: 查询今日未处置的高危及严重事件
        step1_result = await self._step1_query_incidents(
            auth_code=auth_code,
            base_url=base_url
        )

        if not step1_result["success"]:
            return {
                "success": False,
                "step": 1,
                "error": step1_result.get("error"),
                "message": f"查询今日高危事件失败: {step1_result.get('message', '未知错误')}"
            }

        incidents = step1_result.get("incidents", [])
        if not incidents:
            # 无事件需要处理
            return {
                "success": True,
                "completed": True,
                "step": 1,
                "message": "✅ 今日暂无未处置的高危事件，无需处置",
                "data": {
                    "step1": step1_result,
                    "step2": None,
                    "step3": None,
                    "incident_ids": [],
                    "ips_to_block": []
                }
            }

        # Step 2: 分析Top 10事件 - 并行调用事件详情和IP实体
        # 取前10个事件（如果不足10个，取全部）
        top_incidents = incidents[:10]
        step2_result = await self._step2_analyze_top_incidents(
            auth_code=auth_code,
            base_url=base_url,
            incidents=top_incidents,
            provider=provider,
            api_key=api_key,
            llm_base_url=llm_base_url
        )

        if not step2_result["success"]:
            return {
                "success": False,
                "step": 2,
                "error": step2_result.get("error"),
                "incident_ids": [inc.get("uuId") for inc in top_incidents],
                "message": f"获取事件详情失败: {step2_result.get('message', '未知错误')}"
            }

        # Step 3: 提取需要封禁的IP和生成确认信息
        step3_result = self._step3_prepare_confirmation_for_top_incidents(
            step2_result=step2_result,
            incidents=top_incidents
        )

        # 返回前三步的结果，等待用户确认
        return {
            "success": True,
            "completed": False,
            "step": 3,
            "awaiting_confirmation": True,
            "message": f"已分析Top {len(top_incidents)}事件，找到 {len(step3_result.get('ips_to_block', []))} 个需要封禁的IP",
            "data": {
                "step1": {
                    "incidents": incidents,
                    "total": step1_result.get("total", 0)
                },
                "step2": step2_result,
                "step3": step3_result,
                "incident_ids": [inc.get("uuId") for inc in top_incidents],
                "ips_to_block": step3_result.get("ips_to_block", [])
            }
        }

    async def confirm_and_execute(
        self,
        auth_code: str,
        base_url: str,
        incident_id: str = None,
        incident_ids: List[str] = None,
        ips_to_block: List[str] = None,
        device_name: str = "物联网安全网关",
        block_duration_days: int = 7
    ) -> Dict[str, Any]:
        """
        步骤4: 用户确认后执行封禁和状态更新 (并行执行)

        Args:
            auth_code: Flux认证码
            base_url: Flux API地址
            incident_id: 单个事件ID（向后兼容）
            incident_ids: 事件ID列表（Top 10场景）
            ips_to_block: 要封禁的IP列表
            device_name: 封禁设备名称 (默认: 物联网安全网关)
            block_duration_days: 封禁天数 (默认: 7天)

        Returns:
            执行结果字典
        """
        # 兼容旧版本：如果只传了incident_id，转换为列表
        if incident_id and not incident_ids:
            incident_ids = [incident_id]

        if not incident_ids:
            incident_ids = []

        if ips_to_block is None:
            ips_to_block = []

        # 如果没有IP需要封禁，只更新事件状态
        if not ips_to_block:
            update_results = []
            for incident_id in incident_ids:
                result = await self._update_incident_status(
                    auth_code=auth_code,
                    base_url=base_url,
                    incident_id=incident_id
                )
                update_results.append(result)

            return {
                "success": all(r.get("success", False) for r in update_results),
                "completed": True,
                "step": 4,
                "message": f"已更新 {len(incident_ids)} 个事件的状态",
                "results": {
                    "ip_block": {
                        "total": 0,
                        "success": 0,
                        "failed": 0,
                        "details": []
                    },
                    "incident_updates": update_results
                }
            }

        # 并行执行IP封禁和事件状态更新
        block_tasks = []
        for ip in ips_to_block:
            task = self._block_ip(
                auth_code=auth_code,
                base_url=base_url,
                ip=ip,
                device_name=device_name,
                duration_days=block_duration_days
            )
            block_tasks.append(task)

        # 为每个事件创建更新任务
        update_tasks = []
        for incident_id in incident_ids:
            task = self._update_incident_status(
                auth_code=auth_code,
                base_url=base_url,
                incident_id=incident_id
            )
            update_tasks.append(task)

        # 并行执行所有任务
        all_results = await asyncio.gather(
            *block_tasks,
            *update_tasks,
            return_exceptions=True
        )

        # 解析结果
        block_results = all_results[:len(ips_to_block)]
        update_results = all_results[len(ips_to_block):]

        # 统计成功/失败
        block_success_count = 0
        block_failed_count = 0
        block_details = []

        for i, result in enumerate(block_results):
            ip = ips_to_block[i]
            if isinstance(result, Exception):
                block_failed_count += 1
                block_details.append({
                    "ip": ip,
                    "success": False,
                    "error": str(result)
                })
            elif result.get("success"):
                block_success_count += 1
                block_details.append({
                    "ip": ip,
                    "success": True,
                    "rule_ids": result.get("rule_ids", []),
                    "message": result.get("message", "")
                })
            else:
                block_failed_count += 1
                block_details.append({
                    "ip": ip,
                    "success": False,
                    "error": result.get("message", "未知错误")
                })

        # 统计事件更新成功/失败
        update_success_count = 0
        update_failed_count = 0

        for result in update_results:
            if isinstance(result, dict) and result.get("success"):
                update_success_count += 1
            else:
                update_failed_count += 1

        update_success = update_success_count > 0

        # 判断整体成功状态
        overall_success = (block_success_count > 0 or len(ips_to_block) == 0) and update_success

        # 构建返回消息
        if block_success_count == len(ips_to_block) and update_success_count == len(update_results):
            message = f"✅ 每日高危事件闭环完成\n• IP封禁: {block_success_count}/{len(ips_to_block)} 成功\n• 事件处置: {update_success_count}/{len(update_results)} 成功"
        elif block_success_count > 0 or update_success_count > 0:
            message = f"⚠️ 部分成功\n• IP封禁: {block_success_count}/{len(ips_to_block)} 成功\n• 事件处置: {update_success_count}/{len(update_results)} 成功"
        else:
            message = f"❌ 执行失败\n• IP封禁: {block_success_count}/{len(ips_to_block)} 成功\n• 事件处置: {update_success_count}/{len(update_results)} 成功"

        return {
            "success": overall_success,
            "completed": True,
            "step": 4,
            "message": message,
            "partial_success": (block_success_count > 0 and block_failed_count > 0) or (block_success_count > 0 and update_failed_count > 0),
            "results": {
                "ip_block": {
                    "total": len(ips_to_block),
                    "success": block_success_count,
                    "failed": block_failed_count,
                    "details": block_details
                },
                "incident_updates": {
                    "total": len(update_results),
                    "success": update_success_count,
                    "failed": update_failed_count,
                    "details": update_results
                }
            }
        }

    async def _step1_query_incidents(
        self,
        auth_code: str,
        base_url: str
    ) -> Dict[str, Any]:
        """
        步骤1: 查询今天所有未处置的高危及严重事件

        Returns:
            {
                "success": bool,
                "incidents": list,
                "total": int,
                "error": str (optional)
            }
        """
        try:
            # 计算今天的时间范围（今天00:00:00到23:59:59）
            now = datetime.now()
            start_of_day = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)

            start_timestamp = int(start_of_day.timestamp())
            end_timestamp = int(end_of_day.timestamp())

            result = await self.incidents_service.get_incidents(
                auth_code=auth_code,
                base_url=base_url,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                time_field="endTime",
                severities=[3, 4],  # 高危[3]和严重[4]
                deal_status=[0],     # 未处置[0]
                page_size=20,
                page=1,
                sort="severity:desc,endTime:desc"  # 按严重等级降序，时间降序
            )

            if result.get("success"):
                # 安全获取data和item，确保不为None
                data = result.get("data") or {}
                items = data.get("item") or []

                return {
                    "success": True,
                    "incidents": items,
                    "total": len(items)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "查询失败"),
                    "incidents": [],
                    "total": 0
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "incidents": [],
                "total": 0
            }

    async def _step2_analyze_incident(
        self,
        auth_code: str,
        base_url: str,
        incident_id: str
    ) -> Dict[str, Any]:
        """
        步骤2: 并行获取事件详情和IP实体

        Returns:
            {
                "success": bool,
                "proof": dict,
                "entities": dict,
                "error": str (optional)
            }
        """
        try:
            # 并行调用
            proof_task = self.incidents_service.get_incident_proof(
                auth_code=auth_code,
                base_url=base_url,
                uuid=incident_id
            )

            entities_task = self.incidents_service.get_incident_entities_ip(
                auth_code=auth_code,
                base_url=base_url,
                uuid=incident_id
            )

            proof_result, entities_result = await asyncio.gather(
                proof_task,
                entities_task,
                return_exceptions=True
            )

            # 检查proof结果
            proof_success = isinstance(proof_result, dict) and proof_result.get("success")
            # 确保proof_data不为None
            proof_data = proof_result.get("data") if proof_success else {}
            proof_error = proof_result.get("message") if isinstance(proof_result, dict) else str(proof_result)

            # 检查entities结果 - 修复None处理
            entities_success = isinstance(entities_result, dict) and entities_result.get("success")
            entities_data = None
            entities_error = None

            if entities_success:
                # 成功时获取data，确保不为None
                entities_data = entities_result.get("data") or {}
            else:
                # 失败时设置默认空字典
                entities_data = {}
                if isinstance(entities_result, dict):
                    entities_error = entities_result.get("message", "获取失败")
                else:
                    entities_error = str(entities_result) if entities_result else "未知错误"

            # 组合结果
            overall_success = proof_success and entities_success

            return {
                "success": overall_success,
                "proof": proof_data,
                "entities": entities_data,
                "error": (
                    f"详情获取失败: {proof_error}" if not proof_success else
                    f"IP实体获取失败: {entities_error}" if not entities_success else None
                )
            }
        except Exception as e:
            return {
                "success": False,
                "proof": {},  # 返回空字典而不是None
                "entities": {},  # 返回空字典而不是None
                "error": str(e)
            }

    async def _evaluate_incident_risk(
        self,
        incident: Dict[str, Any],
        proof: Dict[str, Any],
        entities: Dict[str, Any],
        provider: str = None,
        api_key: str = None,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用大模型评估事件危害程度

        Args:
            incident: 事件信息
            proof: 事件详情
            entities: IP实体信息
            provider: LLM提供商
            api_key: LLM API密钥
            llm_base_url: LLM API地址

        Returns:
            {
                "risk_level": int,  # 0-4: 未知、低危、中危、高危、严重
                "risk_reasoning": str,  # 评估理由
                "recommendation": str  # 处置建议
            }
        """
        try:
            # 如果没有配置LLM，使用规则评估
            if not provider or not api_key:
                return self._evaluate_incident_risk_by_rules(incident, proof, entities)

            from .llm_service import LLMService
            llm_service = LLMService()

            # 构造评估prompt
            incident_name = incident.get("name", "")
            host_ip = incident.get("hostIp", "")
            severity = incident.get("severity", 0)

            # 提取攻击时间线信息
            timelines = proof.get("incidentTimeLines", []) or []
            timeline_summary = "\n".join([
                f"- {t.get('stage', '')}: {t.get('time', '')}"
                for t in timelines[-5:]  # 最近5条
            ]) if timelines else "无"

            # 提取IP实体信息
            ip_entities = entities.get("item") or []
            ip_summary = []
            for entity in ip_entities[:5]:  # 最多5个IP
                ip = entity.get("ip", "")
                threat_level = entity.get("threatLevel", 0)
                ndr_status = entity.get("ndrDealStatusInfo", {}).get("status", "")
                threat_desc = ["未知", "低危", "中危", "高危", "严重"]
                ip_summary.append(f"  IP: {ip}, 威胁等级: {threat_desc[threat_level] if threat_level < len(threat_desc) else '未知'}, 封禁状态: {ndr_status}")

            ip_text = "\n".join(ip_summary) if ip_summary else "  无外网IP实体"

            evaluation_prompt = f"""你是一个网络安全专家。请分析以下安全事件并评估其危害程度。

## 事件信息
- 事件名称: {incident_name}
- 主机IP: {host_ip}
- 原始严重等级: {severity}

## 攻击时间线（最近5条）
{timeline_summary}

## 外网IP实体
{ip_text}

## 评估标准
- **严重 (4分)**: 已有明确的攻击行为，如恶意代码执行、数据窃取、横向移动等，且外网IP存在高威胁情报
- **高危 (3分)**: 有可疑行为，疑似攻击正在发生或已发生，外网IP存在威胁情报
- **中危 (2分)**: 存在安全风险或异常行为，但攻击性质不明确，或外网IP威胁等级较低
- **低危 (1分)**: 异常行为可能是误报，外网IP威胁等级低或无威胁情报
- **未知 (0分)**: 信息不足以判断

请返回JSON格式（只返回JSON，不要其他内容）:
{{
  "risk_level": 0-4,
  "risk_reasoning": "评估理由，简明扼要（50字以内）",
  "recommendation": "处置建议（30字以内）"
}}"""

            # 调用LLM进行评估
            response = await llm_service.chat(
                messages=[{"role": "user", "content": evaluation_prompt}],
                provider=provider,
                api_key=api_key,
                base_url=llm_base_url
            )

            if response.get("success"):
                import re
                import json
                response_text = response.get("message", "")

                # 提取JSON
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        risk_level = result.get("risk_level", 0)
                        # 确保风险等级在0-4范围内
                        if isinstance(risk_level, int) and 0 <= risk_level <= 4:
                            return {
                                "risk_level": risk_level,
                                "risk_reasoning": result.get("risk_reasoning", "基于事件信息和威胁情报分析"),
                                "recommendation": result.get("recommendation", "建议进一步调查和处置")
                            }
                    except (json.JSONDecodeError, KeyError):
                        pass

            # LLM评估失败，回退到规则评估
            return self._evaluate_incident_risk_by_rules(incident, proof, entities)

        except Exception as e:
            # 异常情况，使用规则评估
            return self._evaluate_incident_risk_by_rules(incident, proof, entities)

    def _evaluate_incident_risk_by_rules(
        self,
        incident: Dict[str, Any],
        proof: Dict[str, Any],
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """基于规则评估事件危害程度"""
        severity = incident.get("severity", 0) or 0

        # 提取IP实体信息
        ip_entities = entities.get("item") or []

        # 统计威胁IP数量和威胁等级
        high_threat_ips = 0
        max_threat_level = 0

        for entity in ip_entities:
            threat_level = entity.get("threatLevel", 0) or 0
            if threat_level >= 3:
                high_threat_ips += 1
            max_threat_level = max(max_threat_level, threat_level)

        # 基于规则计算风险等级
        # 基础风险 = 事件原始严重等级 (0-4)
        # 如果有高危IP，增加风险等级
        risk_level = severity

        if high_threat_ips > 0:
            risk_level = min(4, risk_level + 1)
        elif max_threat_level >= 2:
            risk_level = max(1, risk_level)

        # 生成评估理由
        risk_desc = ["未知", "低危", "中危", "高危", "严重"]
        reasoning = f"事件严重等级: {risk_desc[severity] if severity < len(risk_desc) else '未知'}"

        if high_threat_ips > 0:
            reasoning += f", 检测到 {high_threat_ips} 个高威胁IP"
        elif ip_entities:
            reasoning += f", 共 {len(ip_entities)} 个外网IP实体"
        else:
            reasoning += ", 无外网IP实体"

        # 生成处置建议
        if risk_level >= 3:
            recommendation = "建议立即处置威胁IP并更新事件状态"
        elif risk_level >= 2:
            recommendation = "建议调查并确认后处置"
        else:
            recommendation = "建议监控并持续观察"

        return {
            "risk_level": risk_level,
            "risk_reasoning": reasoning,
            "recommendation": recommendation
        }

    async def _step2_analyze_top_incidents(
        self,
        auth_code: str,
        base_url: str,
        incidents: List[Dict[str, Any]],
        provider: str = None,
        api_key: str = None,
        llm_base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        步骤2: 并行分析Top 10事件

        Args:
            auth_code: Flux认证码
            base_url: Flux API地址
            incidents: 事件列表
            provider: LLM提供商（用于危害评估）
            api_key: LLM API密钥（用于危害评估）
            llm_base_url: LLM API地址（用于危害评估）

        Returns:
            {
                "success": bool,
                "incident_details": list,  # 每个事件的详情和实体
                "error": str (optional)
            }
        """
        try:
            # 并行获取所有事件的详情和IP实体
            tasks = []
            for incident in incidents:
                task = self._step2_analyze_incident(
                    auth_code=auth_code,
                    base_url=base_url,
                    incident_id=incident.get("uuId")
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 组合结果
            incident_details = []
            overall_success = True
            error_messages = []

            for i, result in enumerate(results):
                incident_info = {
                    "incident": incidents[i],
                    "proof": None,
                    "entities": None,
                    "success": False,
                    "error": None
                }

                if isinstance(result, Exception):
                    incident_info["error"] = str(result)
                    error_messages.append(f"事件{incidents[i].get('name', '未知')}失败: {str(result)}")
                    overall_success = False
                elif result.get("success"):
                    incident_info["proof"] = result.get("proof")
                    incident_info["entities"] = result.get("entities")
                    incident_info["success"] = True

                    # 评估危害程度
                    try:
                        risk_assessment = await self._evaluate_incident_risk(
                            incident=incidents[i],
                            proof=result.get("proof") or {},
                            entities=result.get("entities") or {},
                            provider=provider,
                            api_key=api_key,
                            llm_base_url=llm_base_url
                        )
                        incident_info["risk_assessment"] = risk_assessment
                    except Exception as e:
                        # 评估失败，使用默认值
                        incident_info["risk_assessment"] = {
                            "risk_level": 0,
                            "risk_reasoning": "评估失败",
                            "recommendation": "建议人工审核"
                        }
                else:
                    incident_info["error"] = result.get("error")
                    error_messages.append(f"事件{incidents[i].get('name', '未知')}失败: {result.get('error', '未知错误')}")
                    overall_success = False

                incident_details.append(incident_info)

            # 至少有一个成功就算部分成功
            return {
                "success": any(inc["success"] for inc in incident_details),
                "incident_details": incident_details,
                "error": "; ".join(error_messages) if error_messages else None
            }
        except Exception as e:
            return {
                "success": False,
                "incident_details": [],
                "error": str(e)
            }

    def _step3_prepare_confirmation_for_top_incidents(
        self,
        step2_result: Dict[str, Any],
        incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        步骤3: 为Top 10事件提取需要封禁的IP和生成确认信息

        Returns:
            {
                "ips_to_block": list,
                "ip_details": list,
                "ai_summary": str,
                "incident_summaries": list  # 每个事件的摘要
            }
        """
        # 收集所有需要封禁的IP
        ips_to_block = []
        ip_details = []
        incident_summaries = []
        total_ips = 0  # 总IP数
        blocked_ips = 0  # 已封禁IP数
        unblocked_ips = 0  # 未封禁IP数

        for incident_detail in step2_result.get("incident_details", []):
            if not incident_detail.get("success"):
                continue

            incident = incident_detail.get("incident", {})
            entities_data = incident_detail.get("entities") or {}

            # 安全获取item列表
            ip_entities = entities_data.get("item") if isinstance(entities_data, dict) else None
            if not isinstance(ip_entities, list):
                ip_entities = []

            # 筛选未处置的威胁IP
            for entity in ip_entities:
                ndr_status_info = entity.get("ndrDealStatusInfo", {}) or {}
                ndr_status = ndr_status_info.get("status", "")

                # 统计IP总数和封禁状态
                total_ips += 1
                if ndr_status == "BLOCK_SUCCESS":
                    blocked_ips += 1
                else:
                    unblocked_ips += 1

                if ndr_status != "BLOCK_SUCCESS":
                    ip_address = entity.get("ip", "")
                    threat_level = entity.get("threatLevel", 0)
                    location = entity.get("location", "")
                    tags = entity.get("intelligenceTag", []) or []

                    # 避免重复添加相同的IP
                    if ip_address and ip_address not in ips_to_block:
                        ips_to_block.append(ip_address)
                        ip_details.append({
                            "ip": ip_address,
                            "threat_level": threat_level,
                            "location": location,
                            "tags": tags,
                            "ndr_status": ndr_status,
                            "incident_id": incident.get("uuId"),
                            "incident_name": incident.get("name")
                        })

            # 生成事件摘要
            incident_summaries.append({
                "incident_id": incident.get("uuId"),
                "incident_name": incident.get("name"),
                "host_ip": incident.get("hostIp"),
                "severity": incident.get("severity"),
                "ip_count": len([e for e in ip_entities if e.get("ndrDealStatusInfo", {}).get("status") != "BLOCK_SUCCESS"])
            })

        # 生成AI分析结论
        ai_summary = ""
        if ip_details:
            top_threat_ip = ip_details[0]
            threat_desc = ["未知", "低危", "中危", "高危", "严重"]
            threat_level_name = threat_desc[top_threat_ip["threat_level"]] if top_threat_ip["threat_level"] < len(threat_desc) else "未知"
            tags_str = ", ".join(top_threat_ip["tags"]) if top_threat_ip["tags"] else "无标签"

            ai_summary = (
                f"已从Top {len(incidents)}事件中确认 {len(ips_to_block)} 个威胁IP，"
                f"最高威胁IP [{top_threat_ip['ip']}] 为{threat_level_name}威胁，"
                f"情报标签: {tags_str}，"
                f"建议立即封禁"
            )
        else:
            # 提供更详细的信息，帮助诊断为什么没有IP需要封禁
            if total_ips == 0:
                ai_summary = f"分析Top {len(incidents)}事件，未发现外网IP实体，建议仅更新事件状态"
            elif blocked_ips == total_ips:
                ai_summary = f"分析Top {len(incidents)}事件，共{total_ips}个威胁IP已全部封禁（状态: BLOCK_SUCCESS），建议仅更新事件状态"
            else:
                # 有未封禁的IP但为空（可能是重复IP或其他原因）
                ai_summary = f"分析Top {len(incidents)}事件，共{total_ips}个IP（已封禁: {blocked_ips}，未封禁: {unblocked_ips}），需要封禁的IP列表为空，建议仅更新事件状态"

        return {
            "ips_to_block": ips_to_block,
            "ip_details": ip_details,
            "ai_summary": ai_summary,
            "incident_summaries": incident_summaries
        }

    def _step3_prepare_confirmation(
        self,
        step2_result: Dict[str, Any],
        incident: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        步骤3: 提取需要封禁的IP和生成确认信息

        Returns:
            {
                "ips_to_block": list,
                "ip_details": list,
                "ai_summary": str,
                "incident_name": str,
                "incident_id": str
            }
        """
        # 安全获取entities_data，确保不为None
        entities_data = step2_result.get("entities") or {}

        # 安全获取item列表，确保是列表类型
        ip_entities = entities_data.get("item") if isinstance(entities_data, dict) else None
        if not isinstance(ip_entities, list):
            ip_entities = []

        # 筛选未处置的威胁IP
        ips_to_block = []
        ip_details = []

        for entity in ip_entities:
            # 检查端侧处置状态
            ndr_status_info = entity.get("ndrDealStatusInfo", {})
            ndr_status = ndr_status_info.get("status", "")

            # 如果未成功封禁，则加入封禁列表
            if ndr_status != "BLOCK_SUCCESS":
                ip_address = entity.get("ip", "")
                threat_level = entity.get("threatLevel", 0)
                location = entity.get("location", "")
                tags = entity.get("intelligenceTag", [])

                ips_to_block.append(ip_address)
                ip_details.append({
                    "ip": ip_address,
                    "threat_level": threat_level,
                    "location": location,
                    "tags": tags,
                    "ndr_status": ndr_status
                })

        # 生成AI分析结论
        ai_summary = ""
        if ip_details:
            top_threat_ip = ip_details[0]
            threat_desc = ["未知", "低危", "中危", "高危", "严重"]
            threat_level_name = threat_desc[top_threat_ip["threat_level"]] if top_threat_ip["threat_level"] < len(threat_desc) else "未知"
            tags_str = ", ".join(top_threat_ip["tags"]) if top_threat_ip["tags"] else "无标签"

            ai_summary = (
                f"已确认IP [{top_threat_ip['ip']}] 为{threat_level_name}威胁，"
                f"情报标签: {tags_str}，"
                f"建议立即封禁"
            )
        else:
            ai_summary = "该事件无外网IP实体或IP已处置，建议仅更新事件状态"

        return {
            "ips_to_block": ips_to_block,
            "ip_details": ip_details,
            "ai_summary": ai_summary,
            "incident_name": incident.get("name", ""),
            "incident_id": incident.get("uuId", "")
        }

    async def _block_ip(
        self,
        auth_code: str,
        base_url: str,
        ip: str,
        device_name: str,
        duration_days: int = 7
    ) -> Dict[str, Any]:
        """
        封禁单个IP

        Returns:
            {
                "success": bool,
                "rule_ids": list,
                "message": str,
                "ip": str
            }
        """
        try:
            # 使用IpBlockService
            ipblock_service = IpBlockService(
                base_url=base_url,
                auth_code=auth_code
            )

            # 调用check_and_block获取封禁参数
            check_result = ipblock_service.check_and_block(
                ip_address=ip,
                device_name=device_name,
                device_type="AF"
            )

            if check_result["action"] == "already_blocked":
                # 已封禁
                return {
                    "success": True,
                    "ip": ip,
                    "already_blocked": True,
                    "rule_ids": [],
                    "message": f"IP {ip} 已被封禁"
                }
            elif check_result["action"] == "need_block":
                # 需要封禁，执行封禁操作
                block_params = check_result["block_params"]

                # 修改封禁时长为指定天数
                block_result = ipblock_service.block_ip(
                    ip_address=ip,
                    device_id=block_params["device_id"],
                    device_name=block_params["device_name"],
                    device_type=block_params["device_type"],
                    device_version=block_params.get("device_version", ""),
                    block_type=block_params["block_type"],
                    time_type="temporary",
                    time_value=duration_days,
                    time_unit="d",
                    reason="AI自动化闭环 - 每日高危事件处置"
                )

                return {
                    "success": block_result.get("success", False),
                    "ip": ip,
                    "already_blocked": False,
                    "rule_ids": block_result.get("rule_ids", []),
                    "message": block_result.get("message", ""),
                    "error_info": block_result.get("error_info")
                }
            else:
                # 错误
                error_info = check_result.get("error_info", {})
                return {
                    "success": False,
                    "ip": ip,
                    "error": error_info.get("friendly_message", "封禁失败"),
                    "error_info": error_info
                }
        except Exception as e:
            return {
                "success": False,
                "ip": ip,
                "error": str(e)
            }

    async def _update_incident_status(
        self,
        auth_code: str,
        base_url: str,
        incident_id: str
    ) -> Dict[str, Any]:
        """
        更新事件状态为已处置

        Returns:
            {
                "success": bool,
                "total": int,
                "succeededNum": int,
                "message": str
            }
        """
        try:
            result = await self.incidents_service.update_incident_status(
                auth_code=auth_code,
                base_url=base_url,
                uuids=[incident_id],
                deal_status=40,  # 已处置
                deal_comment="AI自动化闭环 - IP已封禁"
            )

            if result.get("success"):
                data = result.get("data", {})
                return {
                    "success": True,
                    "total": data.get("total", 1),
                    "succeededNum": data.get("succeededNum", 0),
                    "failedNum": data.get("failedNum", 0),
                    "message": "事件状态更新成功"
                }
            else:
                return {
                    "success": False,
                    "total": 0,
                    "succeededNum": 0,
                    "failedNum": 1,
                    "message": result.get("message", "更新失败")
                }
        except Exception as e:
            return {
                "success": False,
                "total": 0,
                "succeededNum": 0,
                "failedNum": 1,
                "message": f"更新失败: {str(e)}"
            }
