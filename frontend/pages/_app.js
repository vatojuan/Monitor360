// File: frontend/pages/_app.js
import '../styles/globals.css'
import Link from 'next/link'

export default function MyApp({ Component, pageProps }) {
  return (
    <>
      <nav className="bg-white shadow p-4 flex space-x-4">
        <Link href="/" className="hover:underline">
          Topología
        </Link>
        <Link href="/status" className="hover:underline">
          Estado
        </Link>
        <Link href="/trunk" className="hover:underline">
          Troncal
        </Link>
        <Link href="/run" className="hover:underline">
          Test Capacidad
        </Link>
      </nav>
      <Component {...pageProps} />
    </>
  )
}
