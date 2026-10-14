import { useState } from 'react';
import './index.css';
import './components/shared.css';
import { AppHeader } from './components/AppHeader';
import { ToastContainer } from './components/ToastContainer';
import { WorkspaceView } from './views/WorkspaceView';
import { WerEvaluator } from './components/WerEvaluator';
import { useToast } from './hooks/useToast';
import type { ActiveView } from './types';
import styles from './App.module.css';

export default function App() {
  const [activeView, setActiveView] = useState<ActiveView>('workspace');
  const [evalPrefill, setEvalPrefill] = useState<string | undefined>(undefined);
  const [evalSeq, setEvalSeq] = useState(0);
  const { toasts, show, dismiss } = useToast();

  function handleSendToEval(text: string) {
    setEvalPrefill(text);
    setEvalSeq((n) => n + 1);
    setActiveView('evaluator');
    show('Transcript sent to WER Evaluator', 'info');
  }

  return (
    <>
      <AppHeader activeView={activeView} onViewChange={setActiveView} />

      <main className={styles.main}>
        {activeView === 'workspace' && (
          <WorkspaceView onSendToEval={handleSendToEval} show={show} />
        )}
        {activeView === 'evaluator' && (
          <WerEvaluator key={evalSeq} prefillPred={evalPrefill} show={show} />
        )}
      </main>

      <footer className={styles.footer}>
        <span>VoiceNote AI · faster-whisper (CTranslate2 int8) · spaCy & scikit-learn NLP</span>
        <span>100% Local Processing · Zero External APIs</span>
      </footer>

      <ToastContainer toasts={toasts} onDismiss={dismiss} />
    </>
  );
}
