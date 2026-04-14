import React from "react";
import { Link } from "react-router-dom";

export const Home = () => {
	return (
		<div className="container py-5">
			<div className="row justify-content-center">
				<div className="col-12 col-lg-10">
					<div className="p-4 p-md-5 rounded-4 bg-light border">
						<h1 className="display-5 fw-bold mb-3">Bienvenido a TaskFlow</h1>
						<p className="lead text-secondary mb-4">
							Organiza tu dia, marca prioridades y manten tus tareas bajo control.
						</p>

						<div className="d-flex flex-wrap gap-2">
							<Link to="/register" className="btn btn-dark btn-lg px-4">
								Crear cuenta
							</Link>
						</div>
					</div>
				</div>
			</div>

			<div className="row g-3 mt-1">
				<div className="col-12 col-md-4">
					<div className="card h-100 border-0 shadow-sm">
						<div className="card-body">
							<h5 className="card-title">Paso 1</h5>
							<p className="card-text text-secondary mb-0">
								Registrate para guardar tus tareas y avances.
							</p>
						</div>
					</div>
				</div>
				<div className="col-12 col-md-4">
					<div className="card h-100 border-0 shadow-sm">
						<div className="card-body">
							<h5 className="card-title">Paso 2</h5>
							<p className="card-text text-secondary mb-0">
								Crea tu lista y separa pendientes por prioridad.
							</p>
						</div>
					</div>
				</div>
				<div className="col-12 col-md-4">
					<div className="card h-100 border-0 shadow-sm">
						<div className="card-body">
							<h5 className="card-title">Paso 3</h5>
							<p className="card-text text-secondary mb-0">
								Completa tareas y mide tu progreso semanal.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}; 