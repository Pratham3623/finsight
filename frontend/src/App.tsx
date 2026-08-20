import {
  BarChart3,
  Building2,
  Database,
  LayoutDashboard,
  Activity,
  Sparkles,
  TrendingUp,
  ChevronDown,
} from "lucide-react";

import {
  BrowserRouter,
  Link,
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";

import DashboardPage from "./pages/DashboardPage";
import CompaniesPage from "./pages/CompaniesPage";
import CompanyDetailPage from "./pages/CompanyDetailPage";
import RankingsPage from "./pages/RankingsPage";
import IndustriesPage from "./pages/IndustriesPage";
import AIAnalystPage from "./pages/AIAnalystPage";
import PipelinePage from "./pages/PipelinePage";
import MonitoringPage from "./pages/MonitoringPage";

import "./App.css";

type NavItem = {
  label: string;
  icon: typeof LayoutDashboard;
  path: string;
};

type NavSection = {
  label: string;
  items: NavItem[];
};

const navigation: NavSection[] = [
  {
    label: "Overview",
    items: [
      {
        label: "Dashboard",
        icon: LayoutDashboard,
        path: "/",
      },
    ],
  },
  {
    label: "Research",
    items: [
      {
        label: "Companies",
        icon: Building2,
        path: "/companies",
      },
      {
        label: "Rankings",
        icon: BarChart3,
        path: "/rankings",
      },
      {
        label: "Industries",
        icon: TrendingUp,
        path: "/industries",
      },
    ],
  },
  {
    label: "Intelligence",
    items: [
      {
        label: "AI Analyst",
        icon: Sparkles,
        path: "/ai-analyst",
      },
    ],
  },
  {
    label: "Operations",
    items: [
      {
        label: "Pipeline",
        icon: Activity,
        path: "/pipeline",
      },
      {
        label: "Monitoring",
        icon: Database,
        path: "/monitoring",
      },
    ],
  },
];

function AppShell() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link
          to="/"
          className="brand"
          style={{
            textDecoration: "none",
          }}
        >
          <div className="brand-mark">F</div>

          <div>
            <div className="brand-name">
              FinSight
            </div>

            <div className="brand-caption">
              Financial Intelligence
            </div>
          </div>
        </Link>

        <div className="workspace-selector">
          <div className="workspace-icon">
            <Database size={14} />
          </div>

          <div className="workspace-copy">
            <span className="workspace-label">
              Workspace
            </span>

            <span className="workspace-name">
              FinSight Analytics
            </span>
          </div>

          <ChevronDown size={14} />
        </div>

        <nav className="navigation">
          {navigation.map((section) => (
            <div
              className="nav-section"
              key={section.label}
            >
              <div className="nav-section-label">
                {section.label}
              </div>

              {section.items.map((item) => {
                const Icon = item.icon;

                const active =
                  location.pathname === item.path ||
                  (
                    item.path !== "/" &&
                    location.pathname.startsWith(
                      `${item.path}/`,
                    )
                  );

                return (
                  <Link
                    className={`nav-item ${
                      active
                        ? "nav-item-active"
                        : ""
                    }`}
                    key={item.path}
                    to={item.path}
                  >
                    <Icon
                      size={16}
                      strokeWidth={1.8}
                    />

                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot" />
            <span>API & data healthy</span>
          </div>

          <div className="version">
            FinSight v0.1.0
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">
            <span>
              {location.pathname === "/"
                ? "Overview"
                : "FinSight"}
            </span>

            <span className="breadcrumb-separator">
              /
            </span>

            <strong>
              {getPageName(location.pathname)}
            </strong>
          </div>

          <div className="topbar-actions">
            <button
              className="search-button"
              type="button"
            >
              Search
            </button>

            <Link
              className="ai-button"
              to="/ai-analyst"
            >
              <Sparkles size={15} />
              AI Analyst
            </Link>

            <div className="avatar">
              PD
            </div>
          </div>
        </header>

        <Routes>
          <Route
            path="/"
            element={<DashboardPage />}
          />

          <Route
            path="/companies"
            element={<CompaniesPage />}
          />

          <Route
            path="/companies/:companyId"
            element={<CompanyDetailPage />}
          />

          <Route
            path="/rankings"
            element={<RankingsPage />}
          />

          <Route
            path="/industries"
            element={<IndustriesPage />}
          />

          <Route
            path="/ai-analyst"
            element={<AIAnalystPage />}
          />

          <Route
            path="/pipeline"
            element={<PipelinePage />}
          />

          <Route
            path="/monitoring"
            element={<MonitoringPage />}
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/"
                replace
              />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

function getPageName(path: string): string {
  if (path === "/") {
    return "Dashboard";
  }

  if (path === "/companies") {
    return "Companies";
  }

  if (path.startsWith("/companies/")) {
    return "Company";
  }

  if (path === "/rankings") {
    return "Rankings";
  }

  if (path === "/industries") {
    return "Industries";
  }

  if (path === "/ai-analyst") {
    return "AI Analyst";
  }

  if (path === "/pipeline") {
    return "Pipeline";
  }

  if (path === "/monitoring") {
    return "Monitoring";
  }

  return "Dashboard";
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}
