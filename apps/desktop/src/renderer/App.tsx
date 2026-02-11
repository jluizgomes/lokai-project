import { useEffect } from 'react';
import { Header } from './components/common/Header';
import { StatusBar } from './components/common/StatusBar';
import { ChatContainer } from './components/chat/ChatContainer';
import { ApprovalModal } from './components/chat/ApprovalModal';
import { SettingsPanel } from './components/settings/SettingsPanel';
import { useUIStore } from './stores/ui.store';
import { useChatStore } from './stores/chat.store';

function App() {
  const { showSettings, setShowSettings } = useUIStore();
  const { approvalRequest, setApprovalRequest } = useChatStore();

  useEffect(() => {
    // Listen for focus-input event from main process
    const unsubscribeFocus = window.iara.on.focusInput(() => {
      // Focus will be handled by ChatInput component
    });

    // Listen for open-settings event from main process
    const unsubscribeSettings = window.iara.on.openSettings(() => {
      setShowSettings(true);
    });

    // Listen for approval requests
    const unsubscribeApproval = window.iara.approval.onShowApproval((request) => {
      setApprovalRequest(request);
    });

    return () => {
      unsubscribeFocus();
      unsubscribeSettings();
      unsubscribeApproval();
    };
  }, [setShowSettings, setApprovalRequest]);

  return (
    <div className="flex flex-col h-screen bg-background text-foreground rounded-lg overflow-hidden border border-border shadow-2xl">
      <Header />

      <main className="flex-1 overflow-hidden">
        {showSettings ? (
          <SettingsPanel onClose={() => setShowSettings(false)} />
        ) : (
          <ChatContainer />
        )}
      </main>

      <StatusBar />

      {approvalRequest && (
        <ApprovalModal
          request={approvalRequest}
          onClose={() => setApprovalRequest(null)}
        />
      )}
    </div>
  );
}

export default App;
