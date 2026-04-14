import { useEffect, useState } from "react";
import { createTodo, getTodos, updateTodoStatus } from "../services/todos.services";

export const Todos = () => {
    const [todos, setTodos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [updatingTodoId, setUpdatingTodoId] = useState(null);
    const [newTodoLabel, setNewTodoLabel] = useState("");
    const [creatingTodo, setCreatingTodo] = useState(false);

    useEffect(() => {
        if (!error) return;

        const timeoutId = setTimeout(() => {
            setError(null);
        }, 3000);

        return () => clearTimeout(timeoutId);
    }, [error]);

    useEffect(() => {
        getTodos()
            .then((data) => {
                setTodos(data);
            })
            .catch((err) => {
                setError(err.message || "Failed to load todos");
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    const handleMarkAsDone = async (todoId) => {
        setError(null);
        setUpdatingTodoId(todoId);

        try {
            const updatedTodo = await updateTodoStatus(todoId, true);
            setTodos((prevTodos) =>
                prevTodos.map((todo) => (todo.id === todoId ? updatedTodo : todo))
            );
        } catch (err) {
            setError(err.message || "No se pudo finalizar la tarea");
        } finally {
            setUpdatingTodoId(null);
        }
    };

    const handleCreateTodo = async (event) => {
        event.preventDefault();
        const label = newTodoLabel.trim();

        if (!label) {
            setError("Escribe una tarea antes de guardar");
            return;
        }

        setError(null);
        setCreatingTodo(true);

        try {
            const createdTodo = await createTodo(label);
            setTodos((prevTodos) => [createdTodo, ...prevTodos]);
            setNewTodoLabel("");
        } catch (err) {
            setError(err.message || "No se pudo crear la tarea");
        } finally {
            setCreatingTodo(false);
        }
    };

    return (
        <div className="container py-5">
            <div className="row justify-content-center">
                <div className="col-12 col-lg-8">
                    <h1 className="mb-4">Mis tareas</h1>

                    <form className="mb-4" onSubmit={handleCreateTodo}>
                        <div className="input-group">
                            <input
                                type="text"
                                className="form-control"
                                placeholder="Escribe una nueva tarea"
                                value={newTodoLabel}
                                onChange={(e) => setNewTodoLabel(e.target.value)}
                                disabled={creatingTodo}
                            />
                            <button type="submit" className="btn btn-primary" disabled={creatingTodo}>
                                {creatingTodo ? "Guardando..." : "Agregar"}
                            </button>
                        </div>
                    </form>

                    {loading && <div className="alert alert-info">Cargando tareas...</div>}
                    {error && <div className="alert alert-danger">{error}</div>}

                    {!loading && todos.length === 0 && (
                        <div className="alert alert-secondary">No hay tareas por ahora.</div>
                    )}

                    {!loading && todos.length > 0 && (
                        <ul className="list-group">
                            {todos.map((todo) => (
                                <li
                                    key={todo.id}
                                    className="list-group-item d-flex justify-content-between align-items-center"
                                >
                                    <span className={todo.is_done ? "text-decoration-line-through text-secondary" : ""}>
                                        {todo.label}
                                    </span>
                                    <div className="d-flex align-items-center gap-2">
                                        <span className={`badge ${todo.is_done ? "text-bg-success" : "text-bg-warning"}`}>
                                            {todo.is_done ? "Done" : "Pending"}
                                        </span>
                                        {!todo.is_done && (
                                            <button
                                                type="button"
                                                className="btn btn-sm btn-outline-success"
                                                onClick={() => handleMarkAsDone(todo.id)}
                                                disabled={updatingTodoId === todo.id}
                                            >
                                                {updatingTodoId === todo.id ? "Guardando..." : "Finalizar"}
                                            </button>
                                        )}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>
        </div>
    );
};
