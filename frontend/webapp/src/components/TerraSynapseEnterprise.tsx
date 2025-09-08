<<<<<<< HEAD
        
import { login as apiLogin, register as apiRegister, getDashboard, saveToken } from "../services/api";
import React, { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, BarChart, Bar
} from "recharts";
import {
  Camera, Cloud, Droplets, TrendingUp, AlertTriangle, MapPin, Settings,
  User, Bell, Search, Calendar, Download, Zap, Leaf, DollarSign,
  Activity, Eye, Play, Wind, Thermometer
} from "lucide-react";

/* ===== Tipagem ===== */
type ActiveTab = "dashboard" | "weather" | "satellite" | "market" | "alerts" | "reports" | "settings";

=======
﻿import React, { useEffect, useState } from "react";
import { Leaf, Thermometer, Droplets, Wind } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip,
  BarChart, Bar
} from "recharts";

/* ===== Tipos ===== */
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
interface WeatherData {
  temperature: number;
  humidity: number;
  windSpeed: number;
  pressure: number;
  et0: number;
  rainfall: number;
  condition: string;
}

interface NdviData {
  current: number;
  status: string;
  trend: string;
  color: string;
}

type Alert = {
  id: number;
<<<<<<< HEAD
  type: "warning" | "info" | "error";
=======
  type: "warning" | "info" | "error" | "success";
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
  message: string;
  priority: "low" | "medium" | "high";
  time: string;
};

<<<<<<< HEAD
type WeeklyItem = { day: string; temp: number; humidity: number; et0: number };
type CommodityItem = { name: string; price: number; change: number; color: string };

const TerraSynapseEnterprise: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>("dashboard");
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [ndviData, setNdviData] = useState<NdviData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
=======
/* ===== Dados fake ===== */
type Point = { dia: string; et0: number };
type Comm = { nome: string; preco: number };

const et0Data: Point[] = [
  { dia: "Seg", et0: 4.2 }, { dia: "Ter", et0: 4.8 }, { dia: "Qua", et0: 5.1 },
  { dia: "Qui", et0: 4.6 }, { dia: "Sex", et0: 5.0 }, { dia: "Sáb", et0: 4.3 }, { dia: "Dom", et0: 4.9 },
];

const commoditiesData: Comm[] = [
  { nome: "Soja",  preco: 154 },
  { nome: "Milho", preco: 72  },
  { nome: "Café",  preco: 1060},
];

/* ===== Cards tipados ===== */
type MetricCardProps = {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  value: React.ReactNode;
  delta?: React.ReactNode;
  color?: "green" | "blue" | "orange" | "purple";
};

const MetricCard: React.FC<MetricCardProps> = ({ icon: Icon, title, value, delta, color = "green" }) => (
  <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-xl bg-gradient-to-r ${
        color === "green"  ? "from-green-100 to-green-200" :
        color === "blue"   ? "from-blue-100 to-blue-200" :
        color === "orange" ? "from-orange-100 to-orange-200" : "from-purple-100 to-purple-200"
      }`}>
        <Icon size={22} className="text-gray-700" />
      </div>
      <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">Atualizado</span>
    </div>
    <div className="text-sm text-gray-500">{title}</div>
    <div className="text-2xl font-bold">{value}</div>
    {delta && <div className="text-xs text-gray-500 mt-1">{delta}</div>}
  </div>
);

const AlertCard: React.FC<{ alert: Alert }> = ({ alert }) => (
  <div
    className={`p-4 rounded-xl border-l-4 ${
      alert.type === "warning" ? "bg-orange-50 border-orange-400" :
      alert.type === "error"   ? "bg-red-50 border-red-400" :
      alert.type === "success" ? "bg-green-50 border-green-400" :
                                 "bg-blue-50 border-blue-400"
    }`}
  >
    <div className="flex items-center justify-between">
      <div className="font-medium">{alert.message}</div>
      <div className="text-xs text-gray-500">{alert.time}</div>
    </div>
    <div className="text-xs text-gray-500 mt-1">Prioridade: {alert.priority}</div>
  </div>
);

/* ===== Tela principal ===== */
export default function TerraSynapseEnterprise() {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [ndviData, setNdviData] = useState<NdviData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)

  useEffect(() => {
<<<<<<< HEAD
    const timer = window.setInterval(() => setCurrentTime(new Date()), 1000);

=======
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
    setWeatherData({
      temperature: 24.5,
      humidity: 68,
      windSpeed: 12.3,
      pressure: 1013.2,
<<<<<<< HEAD
      et0: 4.2,
      rainfall: 0,
      condition: "Parcialmente nublado",
=======
      et0: 4.8,
      rainfall: 0.0,
      condition: "Parcialmente nublado"
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
    });

    setNdviData({
      current: 0.75,
      status: "Saudável",
      trend: "+0.02",
      color: "#4CAF50",
    });

    setAlerts([
      { id: 1, type: "warning", message: "ET0 elevada detectada - considere irrigação", priority: "medium", time: "14:30" },
<<<<<<< HEAD
      { id: 2, type: "info",    message: "Condições ideais para aplicação foliar",      priority: "low",    time: "13:45" },
    ]);

    return () => window.clearInterval(timer);
  }, []);

  const commodityData: CommodityItem[] = [
    { name: "Soja",  price: 165.50, change:  2.3, color: "#4CAF50" },
    { name: "Milho", price:  75.80, change: -1.2, color: "#FF5722" },
    { name: "Café",  price: 1089.30, change: 4.1, color: "#795548" },
  ];

  const weeklyData: WeeklyItem[] = [
    { day: "Seg", temp: 22, humidity: 65, et0: 3.8 },
    { day: "Ter", temp: 25, humidity: 58, et0: 4.2 },
    { day: "Qua", temp: 24, humidity: 62, et0: 4.0 },
    { day: "Qui", temp: 26, humidity: 55, et0: 4.5 },
    { day: "Sex", temp: 24, humidity: 68, et0: 4.2 },
    { day: "Sáb", temp: 23, humidity: 72, et0: 3.9 },
    { day: "Dom", temp: 25, humidity: 60, et0: 4.3 },
  ];

  /* ====== UI ====== */
  const LoginForm: React.FC = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md border border-green-100">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-green-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <Leaf className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">TerraSynapse</h2>
          <p className="text-gray-600">Plataforma Enterprise Agtech</p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Email Corporativo</label>
            <input
              type="email"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
              placeholder="seu.email@empresa.com"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Senha</label>
            <input
              type="password"
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
              placeholder="Senha segura"
            />
          </div>

          <button
            onClick={() => setIsLoggedIn(true)}
            className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            Acessar Plataforma
          </button>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Primeira vez? <span className="text-green-600 font-semibold cursor-pointer hover:underline">Criar conta enterprise</span>
          </p>
        </div>
      </div>
    </div>
  );

  type MetricCardProps = {
    icon: React.ComponentType<{ className?: string }>;
    title: string;
    value: string | number | null | undefined;
    delta?: string;
    color?: "green" | "blue" | "orange" | "purple";
  };

  const MetricCard: React.FC<MetricCardProps> = ({ icon: Icon, title, value, delta, color = "green" }) => (
    <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 transform hover:scale-105">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-xl bg-gradient-to-r ${
          color === "green"  ? "from-green-100 to-green-200" :
          color === "blue"   ? "from-blue-100 to-blue-200" :
          color === "orange" ? "from-orange-100 to-orange-200" : "from-purple-100 to-purple-200"
        }`}>
          <Icon className={`w-6 h-6 ${
            color === "green"  ? "text-green-600"  :
            color === "blue"   ? "text-blue-600"   :
            color === "orange" ? "text-orange-600" : "text-purple-600"
          }`} />
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-500 font-medium">{title}</p>
          <p className="text-2xl font-bold text-gray-800">{value}</p>
          {typeof delta === "string" && (
            <p className={`text-sm font-semibold ${
              delta.startsWith("+") ? "text-green-600" :
              delta.startsWith("-") ? "text-red-600"   : "text-gray-600"
            }`}>
              {delta}
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const AlertCard: React.FC<{ alert: Alert }> = ({ alert }) => (
    <div className={`p-4 rounded-xl border-l-4 ${
      alert.type === "warning" ? "bg-orange-50 border-orange-400" :
      alert.type === "error"   ? "bg-red-50 border-red-400"    : "bg-blue-50 border-blue-400"
    } hover:shadow-md transition-all duration-200`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <AlertTriangle className={`w-5 h-5 mt-0.5 ${
            alert.type === "warning" ? "text-orange-500" :
            alert.type === "error"   ? "text-red-500"    : "text-blue-500"
          }`} />
          <div>
            <p className="text-sm font-medium text-gray-800">{alert.message}</p>
            <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
          alert.priority === "high"   ? "bg-red-100 text-red-800"    :
          alert.priority === "medium" ? "bg-orange-100 text-orange-800" : "bg-blue-100 text-blue-800"
        }`}>
          {alert.priority === "high" ? "Alta" : alert.priority === "medium" ? "Média" : "Baixa"}
        </span>
      </div>
    </div>
  );

  const Dashboard: React.FC = () => (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-3xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard Executivo</h1>
            <p className="text-green-100 text-lg">Monitoramento em Tempo Real • Fazenda São João</p>
            <div className="flex items-center mt-4 space-x-6">
              <div className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span className="text-sm">Ribeirão Preto, SP</span>
              </div>
              <div className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span className="text-sm">{currentTime.toLocaleDateString("pt-BR")}</span>
              </div>
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4" />
                <span className="text-sm">Sistema Online</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">
              {currentTime.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
            </div>
            <div className="text-green-100">Atualização contínua</div>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          icon={Thermometer}
          title="Temperatura"
          value={`${weatherData?.temperature ?? "-"}°C`}
          delta={`${weatherData?.humidity ?? "-"}% umidade`}
          color="orange"
        />
        <MetricCard
          icon={Droplets}
          title="ET0"
          value={`${weatherData?.et0 ?? "-"} mm/dia`}
          delta={(weatherData?.et0 ?? 0) > 5 ? "Irrigação recomendada" : "Normal"}
          color="blue"
        />
        <MetricCard
          icon={Leaf}
          title="NDVI"
          value={ndviData?.current ?? "-"}
          delta={`${ndviData?.trend ?? ""} ${ndviData?.status ?? ""}`}
          color="green"
        />
        <MetricCard
          icon={DollarSign}
          title="Receita/ha"
          value="R$ 8.275"
          delta="+12.3% vs mês anterior"
          color="purple"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-800">Tendências Climáticas</h3>
            <div className="flex space-x-2">
              <button className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg font-medium">7 dias</button>
              <button className="px-3 py-1 text-sm text-gray-500 hover:bg-gray-100 rounded-lg">30 dias</button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={weeklyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="day" stroke="#666" />
              <YAxis stroke="#666" />
              <Tooltip contentStyle={{ backgroundColor: "white", border: "1px solid #e5e7eb", borderRadius: 12, boxShadow: "0 10px 25px rgba(0,0,0,0.1)" }}/>
              <Legend />
              <Line type="monotone" dataKey="temp" stroke="#ff6b35" strokeWidth={3} name="Temperatura (°C)" dot={{ fill: "#ff6b35", r: 6 }} />
              <Line type="monotone" dataKey="et0"  stroke="#0ea5e9" strokeWidth={3} name="ET0 (mm)"        dot={{ fill: "#0ea5e9", r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-800">Preços de Commodities</h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Activity className="w-4 h-4" />
              <span>Tempo real</span>
            </div>
          </div>
          <div className="space-y-4">
            {commodityData.map((c, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-200">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: c.color }} />
                  <span className="font-semibold text-gray-800">{c.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-gray-800">R$ {c.price.toFixed(2)}</div>
                  <div className={`text-sm font-semibold ${c.change >= 0 ? "text-green-600" : "text-red-600"}`}>
                    {c.change >= 0 ? "+" : ""}{c.change}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Alerts & Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-gray-800">Centro de Alertas</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Monitoramento ativo</span>
            </div>
          </div>
          <div className="space-y-4">
            {alerts.map((a) => <AlertCard key={a.id} alert={a} />)}
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
          <h3 className="text-xl font-bold text-gray-800 mb-6">Ações Rápidas</h3>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-4 bg-green-50 hover:bg-green-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center space-x-3">
                <Camera className="w-5 h-5 text-green-600" />
                <span className="font-medium text-gray-800">Análise de Imagem</span>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-green-600" />
            </button>
            <button className="w-full flex items-center justify-between p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center space-x-3">
                <Download className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-800">Relatório PDF</span>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
            </button>
            <button className="w-full flex items-center justify-between p-4 bg-purple-50 hover:bg-purple-100 rounded-xl transition-all duration-200 group">
              <div className="flex items-center space-x-3">
                <Zap className="w-5 h-5 text-purple-600" />
                <span className="font-medium text-gray-800">Automatizar</span>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
            </button>
          </div>
        </div>
=======
      { id: 2, type: "info",    message: "Condições ideais para aplicação foliar",      priority: "low",    time: "13:45" }
    ]);

    const timer = window.setInterval(() => {
      setWeatherData(prev => (prev ? { ...prev, et0: +(prev.et0 + (Math.random() - 0.5) * 0.4).toFixed(2) } : prev));
    }, 8000);

    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      {/* Navbar */}
      <div className="w-full flex items-center gap-2 px-5 py-3 shadow-md"
           style={{ background: "var(--ts-green)", color: "#fff" }}>
        <Leaf size={22} />
        <div className="font-bold">TerraSynapse</div>
        <div className="ml-auto opacity-90">V2.0 • Frontend React</div>
      </div>

      {/* Container */}
      <div className="max-w-[1100px] mx-auto px-4 py-6">
        {/* KPIs */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-black/5">
          <div className="flex items-center gap-2 mb-3">
            <h3 className="text-lg font-semibold">Visão Geral</h3>
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ background: "var(--ts-green-2)", color: "#fff" }}>
              TerraSynapse
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <MetricCard
              icon={Thermometer}
              title="Temperatura"
              value={`${weatherData?.temperature ?? "-"}°C`}
              delta={`${weatherData?.humidity ?? "-"}% umidade`}
              color="orange"
            />
            <MetricCard
              icon={Droplets}
              title="ET0"
              value={`${weatherData?.et0 ?? "-"} mm/dia`}
              delta={(weatherData?.et0 ?? 0) > 5 ? "Irrigação recomendada" : "Normal"}
              color="blue"
            />
            <MetricCard
              icon={Leaf}
              title="NDVI"
              value={ndviData?.current ?? "-"}
              delta={`${ndviData?.trend ?? ""} ${ndviData?.status ?? ""}`}
              color="green"
            />
            <MetricCard
              icon={Wind}
              title="Vento"
              value={`${weatherData?.windSpeed ?? "-"} km/h`}
              delta={`${weatherData?.pressure ?? "-"} hPa`}
              color="purple"
            />
          </div>
        </div>

        {/* Gráficos */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-2xl p-5 shadow-sm border border-black/5">
            <h3 className="text-lg font-semibold mb-2">Clima — ET0 (7 dias)</h3>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={et0Data} margin={{ left: 10, right: 10, top: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="dia" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="et0" stroke="var(--ts-green)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-5 shadow-sm border border-black/5">
            <h3 className="text-lg font-semibold mb-2">Mercado — Commodities (R$)</h3>
            <div className="h-[260px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={commoditiesData} margin={{ left: 10, right: 10, top: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="nome" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="preco" fill="var(--ts-green-2)" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Alertas */}
        <div className="mt-4 bg-white rounded-2xl p-5 shadow-sm border border-black/5">
          <h3 className="text-lg font-semibold mb-2">Alertas</h3>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <AlertCard key={alert.id} alert={alert} />
            ))}
          </div>
        </div>
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
      </div>
    </div>
  );
}

<<<<<<< HEAD
  const Sidebar: React.FC = () => (
    <div className="bg-white shadow-xl border-r border-gray-200 h-full">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-green-700 rounded-xl flex items-center justify-center">
            <Leaf className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">TerraSynapse</h2>
            <p className="text-sm text-gray-600">Enterprise</p>
          </div>
        </div>
      </div>

      <nav className="p-4">
        <div className="space-y-2">
          {[
            { id: "dashboard", label: "Dashboard",      icon: Activity },
            { id: "weather",   label: "Clima",          icon: Cloud },
            { id: "satellite", label: "Satélite",       icon: Eye },
            { id: "market",    label: "Mercado",        icon: TrendingUp },
            { id: "alerts",    label: "Alertas",        icon: Bell },
            { id: "reports",   label: "Relatórios",     icon: Download },
            { id: "settings",  label: "Configurações",  icon: Settings },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ActiveTab)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                activeTab === (item.id as ActiveTab)
                  ? "bg-green-50 text-green-700 border-r-3 border-green-600"
                  : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </div>
  );

  if (!isLoggedIn) return <LoginForm />;

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-64 flex-shrink-0">
        <Sidebar />
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">
              {activeTab === "dashboard" ? "Dashboard Executivo" :
               activeTab === "weather"   ? "Monitoramento Climático" :
               activeTab === "satellite" ? "Análise por Satélite" :
               activeTab === "market"    ? "Inteligência de Mercado" : "Configurações"}
            </h1>

            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Buscar..."
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
                />
              </div>
              <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-all duration-200">
                <Bell className="w-5 h-5" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
              </button>
              <button className="flex items-center space-x-2 p-2 text-gray-600 hover:bg-gray-100 rounded-xl transition-all duration-200">
                <User className="w-5 h-5" />
                <span className="font-medium">João Silva</span>
              </button>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-auto p-8">
          {activeTab === "dashboard" ? <Dashboard /> : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Play className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">Módulo em Desenvolvimento</h3>
                <p className="text-gray-600">Esta funcionalidade estará disponível na próxima versão.</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default TerraSynapseEnterprise;
=======
>>>>>>> d68731b (fix(frontend): tipagem TS do TerraSynapseEnterprise + Tailwind pronto)
