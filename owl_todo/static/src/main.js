
import { registry } from "@web/core/registry";
import { TodoApp } from "./components/todo_app/todo_app";
import { Counter } from "./components/counter/counter";

registry.category("actions").add("owl_todo.action_todo_app", TodoApp);
registry.category("actions").add("owl_todo.action_counter_app",Counter);
