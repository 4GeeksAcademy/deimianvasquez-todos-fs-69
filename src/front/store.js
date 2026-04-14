export const initialStore = () => {
  const token = localStorage.getItem("access_token");
  const user = JSON.parse(localStorage.getItem("user") || "null");
  return {
    message: null,
    todos: [
      {
        id: 1,
        title: "Make the bed",
        background: null,
      },
      {
        id: 2,
        title: "Do my homework",
        background: null,
      },
    ],
    auth: {
      token,
      user,
      isAuthenticated: Boolean(token),
    },
  };
};

export default function storeReducer(store, action = {}) {
  switch (action.type) {
    case "set_hello":
      return {
        ...store,
        message: action.payload,
      };

    case "add_task":
      const { id, color } = action.payload;

      return {
        ...store,
        todos: store.todos.map((todo) =>
          todo.id === id ? { ...todo, background: color } : todo,
        ),
      };
    case "set_auth":
      return {
        ...store,
        auth: {
          token: action.payload?.token || null,
          user: action.payload?.user || null,
          isAuthenticated: Boolean(action.payload?.token),
        },
      };
    case "clear_auth":
      return {
        ...store,
        auth: {
          token: null,
          user: null,
          isAuthenticated: false,
        },
      };
    default:
      throw Error("Unknown action.");
  }
}
