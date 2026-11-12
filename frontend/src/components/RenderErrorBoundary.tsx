import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { hasError: boolean }

export class RenderErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('FitTrack failed to render this page.', error, errorInfo.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="render-error" role="alert">
          <section>
            <h1>We couldn’t load this page</h1>
            <p>Please reload FitTrack. If this keeps happening, check the browser console for details.</p>
            <button className="primary" onClick={() => window.location.reload()}>Reload page</button>
          </section>
        </main>
      )
    }

    return this.props.children
  }
}
