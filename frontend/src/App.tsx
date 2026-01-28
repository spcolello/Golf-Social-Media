import { Routes, Route, Navigate } from "react-router-dom";
import Feed from "./pages/Feed";
import Account from "./pages/Account";
import Navbar from "./components/NavBar";
import LogIn from "./pages/LogIn";
import CreateUser from "./pages/create-user";


export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Feed />} />
        <Route path="/account" element={<Account />} />
        <Route path="/login" element={<LogIn />} />
        <Route path="/create-account" element={<CreateUser />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

