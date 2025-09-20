'''
Utilities: small helper for optional delays or color utilities.
Currently provides a sleep helper used by callers if needed.
'''
package com.chatdev.robot;
public class Utils {
    public static void sleepMillis(int ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}