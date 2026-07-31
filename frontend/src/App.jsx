// App.jsx
// Root component that mounts the application routing.
// All providers are set up in main.jsx; App.jsx simply renders
// the route tree defined in AppRoute.jsx.

import AppRoute from './routes/AppRoute'
import './App.css'

function App() {
  return <AppRoute />
}

export default App
