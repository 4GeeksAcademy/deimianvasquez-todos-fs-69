import { Link } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Navbar = () => {
	const { store, dispatch } = useGlobalReducer();
	const isAuthenticated = store?.auth?.isAuthenticated;
	const userName = store?.auth?.user?.full_name;

	const handleLogout = () => {
		localStorage.removeItem("access_token");
		localStorage.removeItem("user");
		dispatch({ type: "clear_auth" });
	};



	return (
		<nav className="navbar navbar-expand-md navbar-dark bg-dark">
			<div className="container-fluid">
				<Link className="navbar-brand" to="/">Deimian</Link>
				<button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
					<span className="navbar-toggler-icon"></span>
				</button>
				<div className="collapse navbar-collapse" id="navbarSupportedContent">
					<ul className="navbar-nav ms-auto mb-lg-0">
						<li className="nav-item">
							<Link className="nav-link active" aria-current="page" to="/">Home</Link>
						</li>
						<li className="nav-item">
							<Link className="nav-link" to="/todos">Todos</Link>
						</li>
						{!isAuthenticated && (
							<>
								<li className="nav-item mt-2 mt-md-0 ms-md-2">
									<Link className="btn btn-outline-light px-3" to={"/register"}>Register</Link>
								</li>
								<li className="nav-item mt-2 mt-md-0 ms-md-2">
									<Link className="btn btn-light px-3" to={"/login"}>Login</Link>
								</li>
							</>
						)}
						{isAuthenticated && (
							<>
								<li className="nav-item d-flex align-items-center mt-2 mt-md-0 ms-md-2">
									<Link
										className="text-decoration-none bg-light text-dark rounded-pill px-3 py-1 fw-semibold"
										to="/profile"
									>
										{userName || "User"}
									</Link>
								</li>
								<li className="nav-item mt-2 mt-md-0 ms-md-2">
									<button type="button" className="btn btn-outline-warning px-3" onClick={handleLogout}>
										Logout
									</button>
								</li>
							</>
						)}
					</ul>
				</div>
			</div>
		</nav>
	);
};