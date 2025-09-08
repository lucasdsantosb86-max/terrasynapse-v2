import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend,
  BarChart, Bar
} from "recharts";
import {
  Camera, Cloud, Droplets, TrendingUp, AlertTriangle, MapPin, Settings,
  User, Bell, Search, Calendar, Download, Zap, Leaf, DollarSign,
  Activity, Eye, Play, Wind, Thermometer, ChevronRight
} from "lucide-react";

import {
  login as apiLogin,
  register as apiRegister,
  getDashboard,
  saveToken,
} from "../services/api";

/* ============== Tipos ============== */
type ActiveTab = "dashboard" | "weather" | "satellite" | "market" | "alerts" | "reports" | "settings";

interface WeatherData {
  temperature: number; humidity: number; windSpeed: number; pressure: number;
  et0: number; rainfall: number; condition: string;
}
interface NdviData { current: number; status: string; trend: string; color: string; }

type Alert = {
  id: number;
  type: "warning" | "info" | "error" | "success";
  message: string;
  priority: "low" | "medium" | "high";
  time: string;
};

type WeeklyItem = { day: string; temp: number; humidity: number; et0: number };
type CommodityItem = { name: string; price: number; change: number; color: string };

type MetricCardProps = {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  value: React.ReactNode;
  delta?: React.ReactNode;
  color?: "green" | "blue" | "orange" | "purple";
};

/* ============== Subcomponentes (FORA do principal!) ============== */
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
        {typeof delta !== "undefined" && (
          <p className={`text-sm font-semibold ${
            typeof delta === "string" && delta.startsWith("+") ? "text-green-600" :
            typeof delta === "string" && delta.startsWith("-") ? "text-red-600" : "text-gray-600"
          }`}>{delta}</p>
        )}
      </div>
    </div>
  </div>
);

const AlertCard: React.FC<{ alert: Alert }> = ({ alert }) => (
  <div className={`p-4 rounded-xl border-l-4 ${
    alert.type === "warning" ? "bg-orange-50 border-orange-400" :
    alert.type === "error"   ? "bg-red-50 border-red-400"    :
    alert.type === "success" ? "bg-green-50 border-green-400": "bg-blue-50 border-blue-400"
  } hover:shadow-md transition-all duration-200`}>
    <div className="flex items-start justify-between">
      <div className="flex items-start space-x-3">
        <AlertTriangle className={`w-5 h-5 mt-0.5 ${
          alert.type === "warning" ? "text-orange-500" :
          alert.type === "error"   ? "text-red-500"    :
          alert.type === "success" ? "text-green-600"  : "text-blue-500"
        }`} />
        <div>
          <p className="text-sm font-medium text-gray-800">{alert.message}</p>
          <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
        </div>
      </div>
      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
        alert.priority === "high"   ? "bg-red-100 text-red-800" :
        alert.priority === "medium" ? "bg-orange-100 text-orange-800" : "bg-blue-100 text-blue-800"
      }`}>
        {alert.priority === "high" ? "Alta" : alert.priority === "medium" ? "Média" : "Baixa"}
      </span>
    </div>
  </div>
);

const Sidebar: React.FC<{activeTab: ActiveTab; setActiveTab: (t:ActiveTab)=>void;}> = ({ activeTab, setActiveTab }) => (
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
          { id: "dashboard", label: "Dashboard", icon: Activity },
          { id: "weather",   label: "Clima",      icon: Cloud },
          { id: "satellite", label: "Satélite",   icon: Eye },
          { id: "market",    label: "Mercado",    icon: TrendingUp },
          { id: "alerts",    label: "Alertas",    icon: Bell },
          { id: "reports",   label: "Relatórios", icon: Download },
          { id: "settings",  label: "Configurações", icon: Settings },
        ].map((item) => (
          <button key={item.id}
            onClick={() => setActiveTab(item.id as ActiveTab)}
            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
              activeTab === (item.id as ActiveTab)
                ? "bg-green-50 text-green-700 border-r-4 border-green-600"
                : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
            }`}>
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  </div>
);

const Dashboard: React.FC<{
  currentTime: Date;
  weatherData: WeatherData | null;
  ndviData: NdviData | null;
  alerts: Alert[];
  weeklyData: WeeklyItem[];
  commodityData: CommodityItem[];
}> = ({ currentTime, weatherData, ndviData, alerts, weeklyData, commodityData }) => (
  <div className="space-y-8">
    <div className="bg-gradient-to-r from-green-600 to-green-700 rounded-3xl p-8 text-white">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Dashboard Executivo</h1>
          <p className="text-green-100 text-lg">Monitoramento em Tempo Real • Fazenda São João</p>
          <div className="flex items-center mt-4 space-x-6">
            <div className="flex items-center space-x-2"><MapPin className="w-4 h-4" /><span className="text-sm">Ribeirão Preto, SP</span></div>
            <div className="flex items-center space-x-2"><Calendar className="w-4 h-4" /><span className="text-sm">{currentTime.toLocaleDateString("pt-BR")}</span></div>
            <div className="flex items-center space-x-2"><Activity className="w-4 h-4" /><span className="text-sm">Sistema Online</span></div>
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

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard icon={Thermometer} title="Temperatura"
        value={`${weatherData?.temperature ?? "-"}°C`} delta={`${weatherData?.humidity ?? "-"}% umidade`} color="orange" />
      <MetricCard icon={Droplets} title="ET0"
        value={`${weatherData?.et0 ?? "-"} mm/dia`}
        delta={(weatherData?.et0 ?? 0) > 5 ? "Irrigação recomendada" : "Normal"}
        color="blue" />
      <MetricCard icon={Leaf} title="NDVI"
        value={ndviData?.current ?? "-"} delta={`${ndviData?.trend ?? ""} ${ndviData?.status ?? ""}`} color="green" />
      <MetricCard icon={DollarSign} title="Receita/ha" value="R$ 8.275" delta="+12.3% vs mês anterior" color="purple" />
    </div>

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
          <div className="flex items-center space-x-2 text-sm text-gray-500"><Activity className="w-4 h-4" /><span>Tempo real</span></div>
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
            <div className="flex items-center space-x-3"><Camera className="w-5 h-5 text-green-600" /><span className="font-medium text-gray-800">Análise de Imagem</span></div>
            <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-green-600" />
          </button>
          <button className="w-full flex items-center justify-between p-4 bg-blue-50 hover:bg-blue-100 rounded-xl transition-all duration-200 group">
            <div className="flex items-center space-x-3"><Download className="w-5 h-5 text-blue-600" /><span className="font-medium text-gray-800">Relatório PDF</span></div>
            <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600" />
          </button>
          <button className="w-full flex items-center justify-between p-4 bg-purple-50 hover:bg-purple-100 rounded-xl transition-all duration-200 group">
            <div className="flex items-center space-x-3"><Zap className="w-5 h-5 text-purple-600" /><span className="font-medium text-gray-800">Automatizar</span></div>
            <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
          </button>
        </div>
      </div>
    </div>
  </div>
);

const LoginForm: React.FC<{
  email:string; password:string;
  setEmail:(v:string)=>void; setPassword:(v:string)=>void;
  onLogin:()=>void; authLoading:boolean; authError:string|null; goRegister:()=>void;
}> = ({ email, password, setEmail, setPassword, onLogin, authLoading, authError, goRegister }) => (
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
          <input type="email" value={email} onChange={(e)=>setEmail(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
            placeholder="seu.email@empresa.com" />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">Senha</label>
          <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200"
            placeholder="Senha segura" />
        </div>

        <button type="button" onClick={onLogin} disabled={authLoading}
          className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transform hover:scale-105 transition-all duration-200 shadow-lg">
          {authLoading ? "Entrando..." : "Acessar Plataforma"}
        </button>
        {authError && <p className="text-sm text-red-600 text-center">{authError}</p>}
      </div>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Primeira vez? <span onClick={goRegister} className="text-green-600 font-semibold cursor-pointer hover:underline">Criar conta enterprise</span>
        </p>
      </div>
    </div>
  </div>
);

const RegisterForm: React.FC<{
  name:string; email:string; password:string;
  setName:(v:string)=>void; setEmail:(v:string)=>void; setPassword:(v:string)=>void;
  onRegister:()=>void; authLoading:boolean; authError:string|null; goLogin:()=>void;
}> = ({ name, email, password, setName, setEmail, setPassword, onRegister, authLoading, authError, goLogin }) => (
  <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-100 flex items-center justify-center p-4">
    <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md border border-green-100">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-green-700 rounded-full flex items-center justify-center mx-auto mb-4">
          <Leaf className="w-8 h-8 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-gray-800 mb-2">Criar conta</h2>
        <p className="text-gray-600">Acesso Enterprise TerraSynapse</p>
      </div>

      <div className="space-y-6">
        <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Seu nome"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500" />
        <input type="email" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="seu.email@empresa.com"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500" />
        <input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Senha segura"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500" />
        <button type="button" onClick={onRegister} disabled={authLoading}
          className="w-full bg-gradient-to-r from-green-600 to-green-700 text-white py-3 rounded-xl font-semibold hover:from-green-700 hover:to-green-800 transform hover:scale-105 transition-all duration-200 shadow-lg">
          {authLoading ? "Criando..." : "Criar conta"}
        </button>
        {authError && <p className="text-sm text-red-600 text-center">{authError}</p>}
        <p className="text-sm text-gray-600 text-center">
          Já tem conta? <span onClick={goLogin} className="text-green-600 font-semibold cursor-pointer hover:underline">Fazer login</span>
        </p>
      </div>
    </div>
  </div>
);

/* ============== Componente Principal ============== */
export default function TerraSynapseEnterprise() {
  const [activeTab, setActiveTab] = useState<ActiveTab>("dashboard");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [ndviData, setNdviData] = useState<NdviData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [currentTime, setCurrentTime] = useState<Date>(new Date());

  // Auth
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [name, setName] = useState("");
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  async function handleLogin() {
    try {
      setAuthLoading(true); setAuthError(null);
      const data = await apiLogin(email, password);
      const token = (data as any).access_token || (data as any).token;
      if (!token) throw new Error("Token não retornado");
      saveToken(token);
      setIsLoggedIn(true);
    } catch (e:any) {
      setAuthError(e?.message || "Falha no login");
    } finally { setAuthLoading(false); }
  }

  async function handleRegister() {
    try {
      setAuthLoading(true); setAuthError(null);
      await apiRegister({ name, email, password });
      await handleLogin(); // auto-login
    } catch (e:any) {
      setAuthError(e?.message || "Falha no cadastro");
    } finally { setAuthLoading(false); }
  }

  // Mocks iniciais (não dependem do login)
  useEffect(() => {
    setWeatherData({ temperature: 24.5, humidity: 68, windSpeed: 12.3, pressure: 1013.2, et0: 4.2, rainfall: 0, condition: "Parcialmente nublado" });
    setNdviData({ current: 0.75, status: "Saudável", trend: "+0.02", color: "#4CAF50" });
    setAlerts([
      { id: 1, type: "warning", message: "ET0 elevada detectada - considere irrigação", priority: "medium", time: "14:30" },
      { id: 2, type: "info",    message: "Condições ideais para aplicação foliar",      priority: "low",    time: "13:45" },
    ]);
  }, []);

  // Relógio e fetch reais – só quando logado
  useEffect(() => {
    if (!isLoggedIn) return;
    const clock = window.setInterval(() => setCurrentTime(new Date()), 1000);

    (async () => {
      let lat = -21.1767, lon = -47.8208;
      await new Promise<void>((resolve) => {
        if (!navigator.geolocation) return resolve();
        navigator.geolocation.getCurrentPosition(
          p => { lat = p.coords.latitude; lon = p.coords.longitude; resolve(); },
          () => resolve(), { timeout: 3000 }
        );
      });
      try {
        const data:any = await getDashboard(lat, lon);
        setWeatherData({
          temperature: data?.weather?.temp ?? data?.temperature ?? 24.5,
          humidity: data?.weather?.humidity ?? data?.humidity ?? 60,
          windSpeed: data?.weather?.wind_speed ?? data?.windSpeed ?? 10,
          pressure: data?.weather?.pressure ?? data?.pressure ?? 1013,
          et0: data?.et0 ?? data?.weather?.et0 ?? 4.2,
          rainfall: data?.weather?.rain ?? data?.rainfall ?? 0,
          condition: data?.weather?.description ?? data?.condition ?? "—",
        });
        const ndvi = data?.ndvi ?? data?.vegetation?.ndvi;
        const ndviNum = typeof ndvi === "number" ? ndvi : 0.75;
        setNdviData({
          current: ndviNum,
          status: ndviNum >= 0.7 ? "Saudável" : ndviNum >= 0.4 ? "Atenção" : "Crítico",
          trend: data?.vegetation?.trend ?? "+0.00",
          color: ndviNum >= 0.7 ? "#4CAF50" : ndviNum >= 0.4 ? "#F59E0B" : "#EF4444",
        });
      } catch (err) {
        console.warn("Falha no dashboard; mantendo mocks:", err);
      }
    })();

    return () => window.clearInterval(clock);
  }, [isLoggedIn]);

  const commodityData: CommodityItem[] = [
    { name: "Soja", price: 165.5, change: 2.3, color: "#4CAF50" },
    { name: "Milho", price: 75.8, change: -1.2, color: "#FF5722" },
    { name: "Café", price: 1089.3, change: 4.1, color: "#795548" },
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

  if (!isLoggedIn) {
    return mode === "login" ? (
      <LoginForm
        email={email} password={password}
        setEmail={setEmail} setPassword={setPassword}
        onLogin={handleLogin} authLoading={authLoading} authError={authError}
        goRegister={() => setMode("register")}
      />
    ) : (
      <RegisterForm
        name={name} email={email} password={password}
        setName={setName} setEmail={setEmail} setPassword={setPassword}
        onRegister={handleRegister} authLoading={authLoading} authError={authError}
        goLogin={() => setMode("login")}
      />
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="w-64 flex-shrink-0">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
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
                <input type="text" placeholder="Buscar..."
                  className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 transition-all duration-200" />
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
          {activeTab === "dashboard" ? (
            <Dashboard
              currentTime={currentTime}
              weatherData={weatherData}
              ndviData={ndviData}
              alerts={alerts}
              weeklyData={weeklyData}
              commodityData={commodityData}
            />
          ) : (
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
}
