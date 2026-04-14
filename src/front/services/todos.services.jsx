const API_URL = `${import.meta.env.VITE_BACKEND_URL}`;

export const getTodos = async (token = localStorage.getItem("access_token")) => {
    try {
        const response = await fetch(`${API_URL}/todos`, {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`,
            },
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result?.error || result?.message || "Failed to load todos");
        }

        return Array.isArray(result) ? result : [];
    } catch (error) {
        console.error("Error loading todos:", error);
        throw error;
    }
};

export const createTodo = async (label, token = localStorage.getItem("access_token")) => {
    try {
        const response = await fetch(`${API_URL}/todos`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ label }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result?.error || result?.message || "Failed to create todo");
        }

        return result;
    } catch (error) {
        console.error("Error creating todo:", error);
        throw error;
    }
};

export const updateTodoStatus = async (todoId, isDone, token = localStorage.getItem("access_token")) => {
    try {
        const response = await fetch(`${API_URL}/todos/${todoId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ is_done: isDone }),
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result?.error || result?.message || "Failed to update todo");
        }

        return result;
    } catch (error) {
        console.error("Error updating todo status:", error);
        throw error;
    }
};
