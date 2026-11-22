import { describe, expect, test } from "vitest";
import userReducer from "src/redux/user/reducer";
import { loginUserAC, logoutUserAC, setUserStateAC } from "src/redux/user/action-creators";

describe("user reducer", () => {
    const initial = userReducer(undefined, { type: "@@INIT" } as any);

    test("starts logged out", () => {
        expect(initial.authenticated).toBe(false);
        expect(initial.token).toBeNull();
    });

    test("login, profile, logout", () => {
        let state = userReducer(initial, loginUserAC("abc", "anna"));
        expect(state).toMatchObject({ token: "abc", username: "anna", authenticated: true });
        state = userReducer(state, setUserStateAC({ id: "42", email: "anna@example.com" }));
        expect(state).toMatchObject({ id: "42", email: "anna@example.com", token: "abc" });
        expect(userReducer(state, logoutUserAC())).toEqual(initial);
    });
});
