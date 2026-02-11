import { ArrowLeft, Settings, Shield, Brain, Mic, Info } from 'lucide-react';
import { useUIStore } from '../../stores/ui.store';
import { useSettingsStore } from '../../stores/settings.store';
import { PermissionsTab } from './PermissionsTab';
import { LearningDashboard } from './LearningDashboard';
import { cn } from '../../lib/utils';

interface SettingsPanelProps {
  onClose: () => void;
}

const tabs = [
  { id: 'general' as const, label: 'General', icon: Settings },
  { id: 'permissions' as const, label: 'Permissions', icon: Shield },
  { id: 'learning' as const, label: 'Learning', icon: Brain },
  { id: 'voice' as const, label: 'Voice', icon: Mic },
  { id: 'about' as const, label: 'About', icon: Info },
];

export function SettingsPanel({ onClose }: SettingsPanelProps) {
  const { activeSettingsTab, setActiveSettingsTab } = useUIStore();
  const { llm, updateLLMSettings, hotkey, startOnBoot, setStartOnBoot } = useSettingsStore();

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 p-4 border-b border-border">
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-muted transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="font-semibold">Settings</h2>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-32 border-r border-border p-2 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSettingsTab(tab.id)}
              className={cn(
                'w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                activeSettingsTab === tab.id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              )}
            >
              <tab.icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="flex-1 p-4 overflow-y-auto">
          {activeSettingsTab === 'general' && (
            <div className="space-y-6">
              <section>
                <h3 className="font-medium mb-3">LLM Settings</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-muted-foreground">Provider</label>
                    <select
                      value={llm.provider}
                      onChange={(e) =>
                        updateLLMSettings({ provider: e.target.value as typeof llm.provider })
                      }
                      className="w-full mt-1 px-3 py-2 rounded-lg border border-input bg-background text-sm"
                    >
                      <option value="ollama">Ollama</option>
                      <option value="llama.cpp">llama.cpp</option>
                      <option value="openai">OpenAI (Fallback)</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">Model</label>
                    <input
                      type="text"
                      value={llm.model}
                      onChange={(e) => updateLLMSettings({ model: e.target.value })}
                      className="w-full mt-1 px-3 py-2 rounded-lg border border-input bg-background text-sm"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">
                      Temperature: {llm.temperature}
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={llm.temperature}
                      onChange={(e) =>
                        updateLLMSettings({ temperature: parseFloat(e.target.value) })
                      }
                      className="w-full mt-1"
                    />
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">Ollama Host</label>
                    <input
                      type="text"
                      value={llm.ollamaHost}
                      onChange={(e) => updateLLMSettings({ ollamaHost: e.target.value })}
                      className="w-full mt-1 px-3 py-2 rounded-lg border border-input bg-background text-sm"
                      placeholder="http://localhost:11439"
                    />
                  </div>
                </div>
              </section>

              <section>
                <h3 className="font-medium mb-3">Application</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={startOnBoot}
                      onChange={(e) => setStartOnBoot(e.target.checked)}
                      className="rounded border-input"
                    />
                    <span className="text-sm">Start on system boot</span>
                  </label>

                  <div>
                    <label className="text-sm text-muted-foreground">Hotkey</label>
                    <div className="mt-1 px-3 py-2 rounded-lg border border-input bg-muted text-sm text-muted-foreground">
                      {hotkey}
                    </div>
                  </div>
                </div>
              </section>
            </div>
          )}

          {activeSettingsTab === 'permissions' && <PermissionsTab />}

          {activeSettingsTab === 'learning' && <LearningDashboard />}

          {activeSettingsTab === 'voice' && (
            <div className="space-y-6">
              <section>
                <h3 className="font-medium mb-3">Voice Settings</h3>
                <p className="text-sm text-muted-foreground">
                  Voice features coming soon. This will include wake word detection,
                  speech-to-text, and text-to-speech capabilities.
                </p>
              </section>
            </div>
          )}

          {activeSettingsTab === 'about' && (
            <div className="space-y-6">
              <section className="text-center">
                <div className="text-6xl mb-4">🤖</div>
                <h3 className="text-xl font-bold">IARA</h3>
                <p className="text-sm text-muted-foreground">
                  Intelligent Adaptive Runtime Assistant
                </p>
                <p className="text-xs text-muted-foreground mt-2">Version 0.1.0</p>
              </section>

              <section>
                <h4 className="font-medium mb-2">About</h4>
                <p className="text-sm text-muted-foreground">
                  IARA is a desktop AI assistant that runs 100% locally on your machine.
                  It combines natural language processing with OS automation to help you
                  with development tasks, file management, and more.
                </p>
              </section>

              <section>
                <h4 className="font-medium mb-2">Technologies</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Electron + React + TypeScript</li>
                  <li>• Python + LangChain + LangGraph</li>
                  <li>• Ollama for local LLMs</li>
                  <li>• PostgreSQL + Qdrant + Neo4j</li>
                </ul>
              </section>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
