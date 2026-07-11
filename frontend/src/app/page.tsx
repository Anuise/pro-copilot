"use client";

import React, { useState, useEffect } from "react";
import {
  Briefcase,
  BookOpen,
  RefreshCw,
  FileText,
  Activity,
  Calendar,
  Code,
  Mic,
  Database,
  Search,
  Copy,
  Download,
  Check,
  ChevronRight,
  TrendingUp,
  Cpu,
  Loader2,
  AlertCircle
} from "lucide-react";

// 簡易的 Markdown 渲染器元件，用來在 UI 上呈現漂亮的排版
const MarkdownRenderer = ({ content }: { content: string }) => {
  if (!content) return <p className="text-gray-400 italic">無內容</p>;

  const lines = content.split("\n");
  return (
    <div className="space-y-3 text-gray-300 leading-relaxed text-sm">
      {lines.map((line, idx) => {
        // Frontmatter 跳過
        if (line.startsWith("---") || line.startsWith("title:") || line.startsWith("tags:") || line.startsWith("created_at:")) {
          return null;
        }

        // 標題 H1, H2, H3
        if (line.startsWith("# ")) {
          return <h1 key={idx} className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mt-6 mb-3 border-b border-gray-800 pb-2">{line.replace("# ", "")}</h1>;
        }
        if (line.startsWith("## ")) {
          return <h2 key={idx} className="text-xl font-semibold text-indigo-300 mt-5 mb-2">{line.replace("## ", "")}</h2>;
        }
        if (line.startsWith("### ")) {
          return <h3 key={idx} className="text-lg font-medium text-blue-300 mt-4 mb-2">{line.replace("### ", "")}</h3>;
        }

        // 清單項目
        if (line.startsWith("- ") || line.startsWith("* ")) {
          const rawText = line.substring(2);
          // 支援粗體 **text**
          const parts = rawText.split("**");
          return (
            <li key={idx} className="list-disc list-inside ml-4 text-gray-300">
              {parts.map((part, pIdx) => pIdx % 2 === 1 ? <strong key={pIdx} className="text-indigo-400 font-semibold">{part}</strong> : part)}
            </li>
          );
        }

        // 粗體轉換的段落
        if (line.trim() === "") return <div key={idx} className="h-2"></div>;

        const parts = line.split("**");
        return (
          <p key={idx}>
            {parts.map((part, pIdx) => pIdx % 2 === 1 ? <strong key={pIdx} className="text-indigo-400 font-semibold">{part}</strong> : part)}
          </p>
        );
      })}
    </div>
  );
};

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dashboard" | "skills" | "cv" | "logs">("dashboard");
  
  // API URL
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // 後端資料 States
  const [skills, setSkills] = useState<any[]>([]);
  const [cvHistory, setCvHistory] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [backendStatus, setBackendStatus] = useState<"connecting" | "online" | "offline">("connecting");

  // UX / UI States
  const [syncingVector, setSyncingVector] = useState(false);
  const [distilling, setDistilling] = useState(false);
  const [generatingCV, setGeneratingCV] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // CV 產生器表單 State
  const [jdTitle, setJdTitle] = useState("");
  const [jdContent, setJdContent] = useState("");
  const [generatedCVResult, setGeneratedCVResult] = useState("");

  // 技能選取狀態
  const [selectedSkill, setSelectedSkill] = useState<any | null>(null);
  const [selectedHistoryCV, setSelectedHistoryCV] = useState<any | null>(null);

  // 載入所有資料
  const fetchData = async () => {
    try {
      // 1. 檢查後端狀態
      const healthRes = await fetch(`${API_BASE}/health`);
      if (healthRes.ok) {
        setBackendStatus("online");
      } else {
        setBackendStatus("offline");
      }

      // 2. 獲取技能 Wiki
      const skillsRes = await fetch(`${API_BASE}/api/skills`);
      if (skillsRes.ok) {
        const skillsData = await skillsRes.json();
        setSkills(skillsData);
        if (skillsData.length > 0 && !selectedSkill) {
          setSelectedSkill(skillsData[0]);
        }
      }

      // 3. 獲取履歷歷史
      const cvRes = await fetch(`${API_BASE}/api/cv/history`);
      if (cvRes.ok) {
        const cvData = await cvRes.json();
        setCvHistory(cvData);
      }

      // 4. 獲取活動日誌
      const logsRes = await fetch(`${API_BASE}/api/skills/logs`);
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setLogs(logsData);
      }

    } catch (error) {
      console.error("無法連接到後端 API", error);
      setBackendStatus("offline");
    }
  };

  useEffect(() => {
    fetchData();
    // 每 15 秒重新拉取狀態
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  // 同步向量庫事件
  const handleSyncVector = async () => {
    setSyncingVector(true);
    try {
      const res = await fetch(`${API_BASE}/api/skills/sync-vector`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        alert(`🎉 向量同步成功！已處理 ${data.synced_count} 個技能 Wiki 卡片。`);
        fetchData();
      } else {
        alert("❌ 同步失敗，請檢查後端日誌。");
      }
    } catch (err) {
      alert("❌ 無法連線至後端 API。");
    } finally {
      setSyncingVector(false);
    }
  };

  // 手動蒸餾工作足跡事件
  const handleDistillData = async () => {
    setDistilling(true);
    try {
      const res = await fetch(`${API_BASE}/api/skills/distill`, { method: "POST" });
      if (res.ok) {
        alert("🎉 技能蒸餾成功！已成功分析最新日誌並更新 Wiki 庫。");
        fetchData();
      } else {
        const errData = await res.json().catch(() => ({}));
        alert(`❌ 蒸餾失敗: ${errData.detail || "請檢查後端日誌。"}`);
      }
    } catch {
      alert("❌ 無法連線至後端 API。");
    } finally {
      setDistilling(false);
    }
  };

  // 產生客製化履歷事件
  const handleGenerateCV = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jdContent.trim() || !jdTitle.trim()) {
      alert("請填寫職缺標題與職缺描述內容！");
      return;
    }

    setGeneratingCV(true);
    setGeneratedCVResult("");
    try {
      const res = await fetch(`${API_BASE}/api/cv/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jd_title: jdTitle,
          jd_content: jdContent
        })
      });

      if (res.ok) {
        const data = await res.json();
        setGeneratedCVResult(data.cv);
        fetchData(); // 重新整理歷史紀錄
      } else {
        alert("❌ 履歷生成失敗，請檢查後端 OpenAI API 金鑰。");
      }
    } catch (err) {
      alert("❌ 連線後端超時或失敗。");
    } finally {
      setGeneratingCV(false);
    }
  };

  // 複製文字至剪貼簿
  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // 下載 Markdown 檔案
  const downloadMarkdown = (filename: string, content: string) => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: "text/plain;charset=utf-8" });
    element.href = URL.createObjectURL(file);
    element.download = filename;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="flex-1 bg-[#0a0b10] text-gray-100 flex flex-col font-sans">
      
      {/* 頂部 Header & 霓虹漸層線 */}
      <header className="border-b border-gray-800 bg-[#0d0e16]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Cpu className="h-5 w-5 text-white animate-pulse" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400">Pro-Copilot</h1>
            <p className="text-xs text-indigo-400 font-medium tracking-wide uppercase">AI 職涯副駕駛</p>
          </div>
        </div>

        {/* 狀態列 */}
        <div className="flex items-center space-x-4">
          <button 
            onClick={fetchData}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 transition-all active:scale-95"
            title="重新載入"
          >
            <RefreshCw className="h-4 w-4" />
          </button>
          
          <div className="flex items-center space-x-2 bg-gray-900/60 border border-gray-800 px-3 py-1.5 rounded-full text-xs">
            <div className={`h-2.5 w-2.5 rounded-full ${
              backendStatus === "online" ? "bg-emerald-500 shadow-lg shadow-emerald-500/50" : 
              backendStatus === "offline" ? "bg-rose-500 shadow-lg shadow-rose-500/50" : "bg-amber-500 animate-pulse"
            }`} />
            <span className="font-semibold text-gray-300">
              {backendStatus === "online" ? "系統連線中" : backendStatus === "offline" ? "中斷連線" : "連線中..."}
            </span>
          </div>
        </div>
      </header>
      
      {/* 霓虹飾條 */}
      <div className="h-[2px] bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 w-full" />

      {/* 主體 Layout */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* 側邊導航 (Sidebar) */}
        <nav className="w-64 bg-[#0d0e16]/60 border-r border-gray-800 p-4 flex flex-col justify-between hidden md:flex">
          <div className="space-y-1.5">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === "dashboard"
                  ? "bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-400 border border-indigo-500/30"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30 border border-transparent"
              }`}
            >
              <Briefcase className="h-5 w-5" />
              <span className="font-medium text-sm">主控制台</span>
            </button>

            <button
              onClick={() => setActiveTab("skills")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === "skills"
                  ? "bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-400 border border-indigo-500/30"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30 border border-transparent"
              }`}
            >
              <BookOpen className="h-5 w-5" />
              <span className="font-medium text-sm">技能 Wiki 庫</span>
            </button>

            <button
              onClick={() => setActiveTab("cv")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === "cv"
                  ? "bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-400 border border-indigo-500/30"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30 border border-transparent"
              }`}
            >
              <FileText className="h-5 w-5" />
              <span className="font-medium text-sm">RAG 履歷生成</span>
            </button>

            <button
              onClick={() => setActiveTab("logs")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeTab === "logs"
                  ? "bg-gradient-to-r from-indigo-500/20 to-purple-500/10 text-indigo-400 border border-indigo-500/30"
                  : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30 border border-transparent"
              }`}
            >
              <Activity className="h-5 w-5" />
              <span className="font-medium text-sm">系統同步日誌</span>
            </button>
          </div>

          {/* 底部系統架構亮點 */}
          <div className="bg-[#121320] border border-gray-800 p-3 rounded-2xl space-y-2">
            <div className="flex items-center space-x-2 text-indigo-400">
              <Database className="h-4 w-4" />
              <span className="text-[10px] font-bold tracking-widest uppercase">系統架構</span>
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>Vector DB</span>
                <span className="text-emerald-400 font-semibold">Qdrant</span>
              </div>
              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>RDBMS</span>
                <span className="text-emerald-400 font-semibold">PostgreSQL</span>
              </div>
              <div className="flex items-center justify-between text-[11px] text-gray-400">
                <span>RAG Retrieval</span>
                <span className="text-indigo-400 font-semibold">Top-5 Embeds</span>
              </div>
            </div>
          </div>
        </nav>

        {/* 主要工作區 (Main Work Area) */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-[#0a0b10] relative">
          
          {/* TAB 1: DASHBOARD */}
          {activeTab === "dashboard" && (
            <div className="space-y-8 animate-fade-in">
              {/* 橫幅 banner */}
              <div className="relative rounded-3xl overflow-hidden bg-gradient-to-r from-indigo-950/40 via-purple-950/20 to-transparent border border-indigo-500/10 p-6 md:p-8">
                <div className="absolute top-0 right-0 h-full w-1/3 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/10 via-transparent to-transparent pointer-events-none" />
                <div className="max-w-xl space-y-4">
                  <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-xs px-3 py-1 rounded-full font-semibold">
                    RAG-Powered AI Copilot
                  </span>
                  <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                    一鍵將工作日誌轉為<br />向量知識庫與精準客製履歷
                  </h2>
                  <p className="text-sm text-gray-400">
                    Pro-Copilot 會自動讀取並清洗你的 GitLab Git commits、Google 行事曆與 Telegram 語音隨筆，並利用 Qdrant 進行語意向量檢索，生成符合目標職缺 JD 的高含金量履歷。
                  </p>
                  
                  <div className="flex flex-wrap gap-3 pt-2">
                    <button
                      onClick={handleSyncVector}
                      disabled={syncingVector}
                      className="flex items-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-sm font-semibold px-5 py-2.5 rounded-xl shadow-lg shadow-indigo-500/20 transition-all hover:shadow-indigo-500/30 active:scale-95 disabled:opacity-50"
                    >
                      {syncingVector ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <RefreshCw className="h-4 w-4" />
                      )}
                      <span>{syncingVector ? "正在同步向量庫..." : "同步向量資料庫"}</span>
                    </button>
                    
                    <button
                      onClick={() => setActiveTab("cv")}
                      className="flex items-center space-x-2 bg-gray-900 border border-gray-800 hover:bg-gray-800/80 text-gray-200 text-sm font-semibold px-5 py-2.5 rounded-xl transition-all"
                    >
                      <FileText className="h-4 w-4 text-purple-400" />
                      <span>前往生成履歷</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* 三格數據卡 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* 卡 1 */}
                <div className="bg-[#0f111a]/80 border border-gray-800 p-5 rounded-2xl flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-xl bg-blue-500/10 flex items-center justify-center border border-blue-500/20">
                    <BookOpen className="h-6 w-6 text-blue-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 font-medium">技能 Wiki 卡片</p>
                    <h3 className="text-2xl font-bold text-white mt-1">{skills.length} 個</h3>
                    <p className="text-[10px] text-gray-500 mt-0.5">儲存於 vault/skills/</p>
                  </div>
                </div>

                {/* 卡 2 */}
                <div className="bg-[#0f111a]/80 border border-gray-800 p-5 rounded-2xl flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-xl bg-purple-500/10 flex items-center justify-center border border-purple-500/20">
                    <FileText className="h-6 w-6 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 font-medium">客製化履歷歷史</p>
                    <h3 className="text-2xl font-bold text-white mt-1">{cvHistory.length} 份</h3>
                    <p className="text-[10px] text-gray-500 mt-0.5">持久化於 PostgreSQL</p>
                  </div>
                </div>

                {/* 卡 3 */}
                <div className="bg-[#0f111a]/80 border border-gray-800 p-5 rounded-2xl flex items-center space-x-4">
                  <div className="h-12 w-12 rounded-xl bg-pink-500/10 flex items-center justify-center border border-pink-500/20">
                    <Activity className="h-6 w-6 text-pink-400" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 font-medium">最近系統同步活動</p>
                    <h3 className="text-2xl font-bold text-white mt-1">{logs.length} 筆</h3>
                    <p className="text-[10px] text-gray-500 mt-0.5">GitLab, 行事曆, 語音</p>
                  </div>
                </div>

              </div>

              {/* 兩欄排版：近期日誌與履歷生成紀錄 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                
                {/* 欄 1: 履歷生成歷史 */}
                <div className="bg-[#0f111a]/60 border border-gray-800 rounded-2xl p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                    <div className="flex items-center space-x-2 text-indigo-400 font-semibold">
                      <FileText className="h-5 w-5" />
                      <span>近期產生的履歷歷史</span>
                    </div>
                    <button 
                      onClick={() => setActiveTab("cv")} 
                      className="text-xs text-gray-400 hover:text-indigo-400 transition-colors"
                    >
                      查看全部
                    </button>
                  </div>

                  {cvHistory.length === 0 ? (
                    <div className="h-48 flex items-center justify-center text-gray-500 text-sm">
                      目前尚無履歷生成紀錄。
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                      {cvHistory.slice(0, 4).map((cv) => (
                        <div 
                          key={cv.id}
                          className="bg-[#121320] border border-gray-800/80 p-3 rounded-xl flex justify-between items-center hover:border-indigo-500/30 transition-all"
                        >
                          <div className="space-y-1">
                            <h4 className="text-sm font-semibold text-gray-200">{cv.jd_title}</h4>
                            <p className="text-[10px] text-gray-500">
                              {new Date(cv.created_at).toLocaleString("zh-TW")}
                            </p>
                          </div>
                          <button
                            onClick={() => {
                              setSelectedHistoryCV(cv);
                              setActiveTab("cv");
                            }}
                            className="p-1 bg-gray-800 text-gray-300 rounded hover:bg-indigo-500 hover:text-white transition-all text-xs flex items-center space-x-1"
                          >
                            <span>檢視</span>
                            <ChevronRight className="h-3 w-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* 欄 2: 近期活動日誌 */}
                <div className="bg-[#0f111a]/60 border border-gray-800 rounded-2xl p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                    <div className="flex items-center space-x-2 text-indigo-400 font-semibold">
                      <Activity className="h-5 w-5" />
                      <span>同步日誌快照</span>
                    </div>
                    <button 
                      onClick={() => setActiveTab("logs")} 
                      className="text-xs text-gray-400 hover:text-indigo-400 transition-colors"
                    >
                      查看全部
                    </button>
                  </div>

                  {logs.length === 0 ? (
                    <div className="h-48 flex items-center justify-center text-gray-500 text-sm">
                      目前尚無同步記錄。
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-[300px] overflow-y-auto pr-1">
                      {logs.slice(0, 4).map((log, idx) => (
                        <div 
                          key={idx}
                          className="bg-[#121320] border border-gray-800/80 p-3 rounded-xl flex items-center justify-between"
                        >
                          <div className="flex items-center space-x-3">
                            <span className={`p-1.5 rounded-lg text-xs font-semibold ${
                              log.category === "gitlab" ? "bg-orange-500/10 text-orange-400 border border-orange-500/20" :
                              log.category === "calendar" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" :
                              "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                            }`}>
                              {log.category.toUpperCase()}
                            </span>
                            <div>
                              <p className="text-xs font-medium text-gray-200 max-w-[200px] truncate">{log.name}</p>
                              <p className="text-[9px] text-gray-500">{log.time}</p>
                            </div>
                          </div>
                          <span className="text-[10px] text-gray-400">
                            {(log.size / 1024).toFixed(2)} KB
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: SKILLS WIKI */}
          {activeTab === "skills" && (
            <div className="h-full flex flex-col space-y-6 animate-fade-in">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-white">技能 Wiki 庫</h2>
                  <p className="text-xs text-gray-400 mt-1">來自 Obsidian vault 且已轉換為向量嵌入的技能卡片</p>
                </div>
                <div className="flex space-x-3">
                  <button
                    onClick={handleDistillData}
                    disabled={distilling}
                    className="flex items-center space-x-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 text-xs px-3.5 py-2 rounded-xl transition-all"
                  >
                    <Cpu className={`h-3.5 w-3.5 ${distilling ? "animate-spin" : ""}`} />
                    <span>{distilling ? "蒸餾中..." : "手動蒸餾工作足跡"}</span>
                  </button>
                  <button
                    onClick={handleSyncVector}
                    disabled={syncingVector}
                    className="flex items-center space-x-2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 hover:bg-indigo-500/20 text-xs px-3.5 py-2 rounded-xl transition-all"
                  >
                    <RefreshCw className={`h-3.5 w-3.5 ${syncingVector ? "animate-spin" : ""}`} />
                    <span>{syncingVector ? "同步中..." : "重新同步向量庫"}</span>
                  </button>
                </div>
              </div>

              {skills.length === 0 ? (
                <div className="flex-1 bg-[#0f111a]/60 border border-gray-800 rounded-2xl flex flex-col items-center justify-center p-8 space-y-3">
                  <AlertCircle className="h-8 w-8 text-gray-500" />
                  <p className="text-sm text-gray-400">尚無技能 Wiki 資料。</p>
                  <p className="text-xs text-gray-500 text-center max-w-sm">請確認 `vault/skills` 目錄下有 Markdown 技能檔案，或是執行 `uv run pro-copilot init` 進行初始化。</p>
                </div>
              ) : (
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
                  
                  {/* 左側技能列表 */}
                  <div className="lg:col-span-1 bg-[#0f111a]/60 border border-gray-800 rounded-2xl flex flex-col overflow-hidden">
                    <div className="p-3 border-b border-gray-800">
                      <div className="relative">
                        <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-500" />
                        <input
                          type="text"
                          placeholder="搜尋技能..."
                          className="w-full bg-gray-900 border border-gray-800 pl-9 pr-4 py-2 rounded-xl text-xs focus:outline-none focus:border-indigo-500 transition-colors"
                        />
                      </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-2 space-y-1">
                      {skills.map((skill) => (
                        <button
                          key={skill.filename}
                          onClick={() => setSelectedSkill(skill)}
                          className={`w-full text-left p-3 rounded-xl border transition-all ${
                            selectedSkill?.filename === skill.filename
                              ? "bg-indigo-500/10 border-indigo-500/30 text-white"
                              : "bg-transparent border-transparent text-gray-400 hover:bg-gray-800/20 hover:text-gray-200"
                          }`}
                        >
                          <h4 className="text-sm font-semibold">{skill.title}</h4>
                          <p className="text-[11px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">{skill.summary}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* 右側技能詳情 (Markdown) */}
                  <div className="lg:col-span-2 bg-[#0f111a]/60 border border-gray-800 rounded-2xl flex flex-col overflow-hidden">
                    {selectedSkill ? (
                      <div className="flex flex-col h-full">
                        <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/20">
                          <div>
                            <h3 className="text-base font-bold text-white">{selectedSkill.title}</h3>
                            <p className="text-[10px] text-gray-500 mt-0.5">檔案: {selectedSkill.filename}</p>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => copyToClipboard(selectedSkill.content, "skill")}
                              className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-all text-xs flex items-center space-x-1"
                            >
                              {copiedId === "skill" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                              <span>{copiedId === "skill" ? "已複製" : "複製"}</span>
                            </button>
                            <button
                              onClick={() => downloadMarkdown(selectedSkill.filename, selectedSkill.content)}
                              className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-all text-xs flex items-center space-x-1"
                            >
                              <Download className="h-3.5 w-3.5" />
                              <span>下載</span>
                            </button>
                          </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-6">
                          <MarkdownRenderer content={selectedSkill.content} />
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex items-center justify-center text-gray-500 text-sm">
                        請點擊左側技能卡片查看內容。
                      </div>
                    )}
                  </div>

                </div>
              )}
            </div>
          )}

          {/* TAB 3: CV GENERATOR */}
          {activeTab === "cv" && (
            <div className="h-full flex flex-col space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-white">RAG 客製化履歷生成</h2>
                <p className="text-xs text-gray-400 mt-1">輸入職缺 JD，Pro-Copilot 將透過 Qdrant 進行語意檢索，僅抓取最相關的 STAR 案例以生成履歷。</p>
              </div>

              <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 overflow-hidden">
                
                {/* 左側輸入區 / 歷史紀錄 */}
                <div className="flex flex-col space-y-6 overflow-y-auto pr-1">
                  
                  {/* 輸入表單 */}
                  <form onSubmit={handleGenerateCV} className="bg-[#0f111a]/60 border border-gray-800 rounded-2xl p-5 space-y-4">
                    <h3 className="text-sm font-bold text-indigo-400 border-b border-gray-800 pb-2">新生成任務</h3>
                    
                    <div className="space-y-1.5">
                      <label className="text-xs text-gray-400 font-semibold">目標職缺標題 (JD Title)</label>
                      <input
                        type="text"
                        required
                        value={jdTitle}
                        onChange={(e) => setJdTitle(e.target.value)}
                        placeholder="例如：Senior Python Backend Engineer - Google"
                        className="w-full bg-gray-900 border border-gray-800 px-4 py-2.5 rounded-xl text-xs focus:outline-none focus:border-indigo-500 transition-colors"
                      />
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs text-gray-400 font-semibold">職缺描述內容 (Job Description)</label>
                      <textarea
                        required
                        value={jdContent}
                        onChange={(e) => setJdContent(e.target.value)}
                        rows={8}
                        placeholder="請在此貼上目標職缺的 JD 描述內容，包含職責與技能需求..."
                        className="w-full bg-gray-900 border border-gray-800 px-4 py-2.5 rounded-xl text-xs focus:outline-none focus:border-indigo-500 transition-colors font-mono"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={generatingCV}
                      className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white font-semibold py-3 rounded-xl transition-all disabled:opacity-50 text-xs shadow-lg shadow-indigo-500/10"
                    >
                      {generatingCV ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          <span>AI 正在匹配向量資料庫並撰寫履歷中...</span>
                        </>
                      ) : (
                        <>
                          <Cpu className="h-4 w-4" />
                          <span>開始 RAG 履歷優化與生成</span>
                        </>
                      )}
                    </button>
                  </form>

                  {/* 歷史履歷 */}
                  <div className="bg-[#0f111a]/60 border border-gray-800 rounded-2xl p-5 flex-1 flex flex-col overflow-hidden min-h-[250px]">
                    <h3 className="text-sm font-bold text-gray-300 border-b border-gray-800 pb-2 mb-3">生成歷史紀錄</h3>
                    <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                      {cvHistory.length === 0 ? (
                        <div className="h-full flex items-center justify-center text-gray-500 text-xs">
                          尚無歷史生成履歷。
                        </div>
                      ) : (
                        cvHistory.map((cv) => (
                          <button
                            key={cv.id}
                            onClick={() => {
                              setSelectedHistoryCV(cv);
                              setGeneratedCVResult(""); // 清除當前生成以顯示歷史
                            }}
                            className={`w-full text-left p-3 rounded-xl border flex items-center justify-between transition-all ${
                              selectedHistoryCV?.id === cv.id && !generatedCVResult
                                ? "bg-indigo-500/10 border-indigo-500/30 text-white"
                                : "bg-gray-900/30 border-gray-800 text-gray-400 hover:bg-gray-800/10"
                            }`}
                          >
                            <div>
                              <h4 className="text-xs font-semibold text-gray-200">{cv.jd_title}</h4>
                              <p className="text-[9px] text-gray-500 mt-1">
                                {new Date(cv.created_at).toLocaleString("zh-TW")}
                              </p>
                            </div>
                            <ChevronRight className="h-4 w-4 text-gray-500" />
                          </button>
                        ))
                      )}
                    </div>
                  </div>

                </div>

                {/* 右側輸出預覽區 */}
                <div className="bg-[#0f111a]/60 border border-gray-800 rounded-2xl flex flex-col overflow-hidden h-full">
                  {generatingCV ? (
                    <div className="flex-1 flex flex-col items-center justify-center space-y-4 text-gray-400">
                      <Loader2 className="h-10 w-10 text-indigo-500 animate-spin" />
                      <div className="text-center space-y-1">
                        <p className="text-sm font-medium">職涯副駕駛正努力撰寫中...</p>
                        <p className="text-[11px] text-gray-500">1. 利用 Embeddings 模型將你的 JD 向量化</p>
                        <p className="text-[11px] text-gray-500">2. 在 Qdrant 資料庫中撈取相似度高的 5 個技能 Wiki 卡片</p>
                        <p className="text-[11px] text-gray-500">3. 調用 LLM 整合 STAR 貢獻進行履歷最佳化</p>
                      </div>
                    </div>
                  ) : generatedCVResult || selectedHistoryCV ? (
                    <div className="flex flex-col h-full">
                      <div className="px-6 py-4 border-b border-gray-800 flex items-center justify-between bg-gray-900/20">
                        <div>
                          <h3 className="text-xs font-bold text-indigo-400 tracking-wider uppercase">產生的履歷 Markdown</h3>
                          <h4 className="text-sm font-bold text-white mt-1">
                            {generatedCVResult ? jdTitle : selectedHistoryCV?.jd_title}
                          </h4>
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => copyToClipboard(generatedCVResult || selectedHistoryCV?.generated_cv, "cv_copy")}
                            className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-all text-xs flex items-center space-x-1"
                          >
                            {copiedId === "cv_copy" ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                            <span>{copiedId === "cv_copy" ? "已複製" : "複製"}</span>
                          </button>
                          <button
                            onClick={() => downloadMarkdown(
                              `${(generatedCVResult ? jdTitle : selectedHistoryCV?.jd_title).replace(/\s+/g, "_")}_CV.md`,
                              generatedCVResult || selectedHistoryCV?.generated_cv
                            )}
                            className="p-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-all text-xs flex items-center space-x-1"
                          >
                            <Download className="h-3.5 w-3.5" />
                            <span>下載</span>
                          </button>
                        </div>
                      </div>
                      <div className="flex-1 overflow-y-auto p-6">
                        <MarkdownRenderer content={generatedCVResult || selectedHistoryCV?.generated_cv} />
                      </div>
                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-500 p-8 text-center space-y-2">
                      <FileText className="h-10 w-10 text-gray-600" />
                      <p className="text-sm">尚無履歷內容</p>
                      <p className="text-xs text-gray-600 max-w-xs">請在左側貼上你要應徵的 JD，或是點選下方的歷史紀錄進行載入預覽。</p>
                    </div>
                  )}
                </div>

              </div>
            </div>
          )}

          {/* TAB 4: SYSTEM LOGS */}
          {activeTab === "logs" && (
            <div className="h-full flex flex-col space-y-6 animate-fade-in">
              <div>
                <h2 className="text-xl font-bold text-white">系統同步日誌</h2>
                <p className="text-xs text-gray-400 mt-1">追蹤來自 GitLab webhook 事件、行事曆同步、與語音備忘錄轉譯的原始記錄</p>
              </div>

              <div className="flex-1 bg-[#0f111a]/60 border border-gray-800 rounded-2xl flex flex-col overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/20 flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-400 tracking-wider uppercase">最近 20 筆系統活動</span>
                  <span className="text-xs text-gray-500">掃描自 {API_BASE}/raw_logs/</span>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {logs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 space-y-2">
                      <Activity className="h-8 w-8 text-gray-600" />
                      <p className="text-sm">尚無任何原始日誌</p>
                      <p className="text-xs text-gray-600">系統尚未收到 GitLab Webhook、或是語音筆記上傳。</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {logs.map((log, idx) => (
                        <div
                          key={idx}
                          className="bg-[#121320] border border-gray-800 p-4 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-3 hover:border-gray-700 transition-colors"
                        >
                          <div className="flex items-start space-x-3.5">
                            <div className="mt-1">
                              <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                                log.category === "gitlab" ? "bg-orange-500/10 text-orange-400 border border-orange-500/20" :
                                log.category === "calendar" ? "bg-blue-500/10 text-blue-400 border border-blue-500/20" :
                                "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                              }`}>
                                {log.category.toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <h4 className="text-xs font-semibold text-gray-200">{log.name}</h4>
                              <p className="text-[10px] text-gray-500 mt-1 flex items-center space-x-1">
                                <span className="font-semibold text-gray-400">{log.description}</span>
                                <span>•</span>
                                <span>檔案大小: {(log.size / 1024).toFixed(2)} KB</span>
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between md:justify-end gap-3 text-right">
                            <span className="text-[11px] text-gray-500 font-mono">{log.time}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      {/* 頁尾 */}
      <footer className="bg-[#0b0c13] border-t border-gray-900 px-6 py-3 text-center text-[10px] text-gray-600 flex flex-col md:flex-row justify-between items-center gap-2">
        <span>© {new Date().getFullYear()} Pro-Copilot 個人職涯副駕駛. All rights reserved.</span>
        <div className="flex items-center space-x-3 text-gray-600">
          <span>Obsidian integration</span>
          <span>•</span>
          <span>Qdrant vector engine</span>
          <span>•</span>
          <span>PostgreSQL ledger</span>
        </div>
      </footer>

    </div>
  );
}
