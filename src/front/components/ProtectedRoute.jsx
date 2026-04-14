
import useGlobalReducer from "../hooks/useGlobalReducer"
import { Navigate, Outlet } from "react-router-dom"

export const ProtectedRoute = ({ children }) => {
    const { store } = useGlobalReducer()
    const isAuthenticated = store?.auth?.isAuthenticated


    if (!isAuthenticated) {
        return <Navigate to={"/login"} />
    }

    return children || <Outlet />
}