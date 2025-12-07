;; ============================================================
;; CAD OBSERVER - AutoCAD LISP Plugin
;; Two-way integration with Claude AI
;; ============================================================
;; 
;; INSTALLATION:
;; 1. Copy this file to your AutoCAD support path
;; 2. Add (load "cad-observer.lsp") to acaddoc.lsp
;; 3. Or load manually: APPLOAD > select this file
;;
;; COMMANDS:
;; CAD-OBSERVER-START  - Start logging session
;; CAD-OBSERVER-STOP   - Stop logging session
;; CAD-OBSERVER-STATUS - Show current status
;; CAD-OBSERVER-TASK   - Check for and execute Claude tasks
;; CAD-OBSERVER-AUTO   - Toggle auto-task checking
;;
;; ============================================================

;; ------------------------------------------------------------
;; CONFIGURATION - Update these paths for your system
;; ------------------------------------------------------------

;; Where to save command logs (Claude reads from here)
(setq *CAD-OBS-LOG-PATH* "C:/CADObserver/logs/")

;; Where Claude places task files (AutoCAD reads from here)
(setq *CAD-OBS-TASK-PATH* "C:/CADObserver/tasks/")

;; Where completed tasks go
(setq *CAD-OBS-DONE-PATH* "C:/CADObserver/done/")

;; Log file name pattern
(setq *CAD-OBS-LOG-FILE* nil)  ; Set when session starts

;; Session state
(setq *CAD-OBS-ACTIVE* nil)
(setq *CAD-OBS-SESSION-ID* nil)
(setq *CAD-OBS-CMD-COUNT* 0)
(setq *CAD-OBS-AUTO-TASK* nil)

;; ------------------------------------------------------------
;; UTILITY FUNCTIONS
;; ------------------------------------------------------------

(defun cad-obs-ensure-dirs ()
  "Create required directories if they don't exist."
  (if (not (vl-file-directory-p *CAD-OBS-LOG-PATH*))
    (vl-mkdir *CAD-OBS-LOG-PATH*))
  (if (not (vl-file-directory-p *CAD-OBS-TASK-PATH*))
    (vl-mkdir *CAD-OBS-TASK-PATH*))
  (if (not (vl-file-directory-p *CAD-OBS-DONE-PATH*))
    (vl-mkdir *CAD-OBS-DONE-PATH*))
)

(defun cad-obs-timestamp ()
  "Return ISO-8601 timestamp."
  (setq dt (rtos (getvar "CDATE") 2 6))
  (strcat
    (substr dt 1 4) "-"
    (substr dt 5 2) "-"
    (substr dt 7 2) "T"
    (substr dt 10 2) ":"
    (substr dt 12 2) ":"
    (substr dt 14 2)
  )
)

(defun cad-obs-session-id ()
  "Generate session ID from timestamp."
  (setq dt (rtos (getvar "CDATE") 2 6))
  (strcat
    (substr dt 1 4)
    (substr dt 5 2)
    (substr dt 7 2) "_"
    (substr dt 10 2)
    (substr dt 12 2)
    (substr dt 14 2)
  )
)

(defun cad-obs-escape-json (str)
  "Escape string for JSON."
  (if (null str)
    "null"
    (progn
      (setq str (vl-string-subst "\\\"" "\"" str))
      (setq str (vl-string-subst "\\n" "\n" str))
      (strcat "\"" str "\"")
    )
  )
)

(defun cad-obs-get-layers ()
  "Get list of layer names."
  (setq layers '())
  (vlax-for layer (vla-get-layers 
    (vla-get-activedocument (vlax-get-acad-object)))
    (setq layers (cons (vla-get-name layer) layers))
  )
  layers
)

(defun cad-obs-get-current-layer ()
  "Get current layer name."
  (getvar "CLAYER")
)

(defun cad-obs-get-drawing-name ()
  "Get current drawing name."
  (getvar "DWGNAME")
)

(defun cad-obs-get-cursor-pos ()
  "Get last cursor position."
  (getvar "LASTPOINT")
)

(defun cad-obs-object-count ()
  "Get total object count in model space."
  (vla-get-count 
    (vla-get-modelspace 
      (vla-get-activedocument (vlax-get-acad-object))))
)

;; ------------------------------------------------------------
;; LOGGING FUNCTIONS
;; ------------------------------------------------------------

(defun cad-obs-log-entry (event-type data)
  "Write a log entry to the session file."
  (if *CAD-OBS-ACTIVE*
    (progn
      (setq log-file (open *CAD-OBS-LOG-FILE* "a"))
      (if log-file
        (progn
          (setq entry
            (strcat
              "{"
              "\"timestamp\":" (cad-obs-escape-json (cad-obs-timestamp)) ","
              "\"session_id\":" (cad-obs-escape-json *CAD-OBS-SESSION-ID*) ","
              "\"event_type\":" (cad-obs-escape-json event-type) ","
              "\"drawing\":" (cad-obs-escape-json (cad-obs-get-drawing-name)) ","
              "\"current_layer\":" (cad-obs-escape-json (cad-obs-get-current-layer)) ","
              "\"object_count\":" (itoa (cad-obs-object-count)) ","
              "\"data\":" data
              "}"
            )
          )
          (write-line entry log-file)
          (close log-file)
          (setq *CAD-OBS-CMD-COUNT* (1+ *CAD-OBS-CMD-COUNT*))
        )
      )
    )
  )
)

(defun cad-obs-log-command (reactor-object command-list)
  "Reactor callback for command start."
  (setq cmd-name (car command-list))
  (setq cursor-pos (cad-obs-get-cursor-pos))
  
  (cad-obs-log-entry "COMMAND_START"
    (strcat
      "{"
      "\"command\":" (cad-obs-escape-json cmd-name) ","
      "\"cursor_x\":" (if cursor-pos (rtos (car cursor-pos) 2 4) "null") ","
      "\"cursor_y\":" (if cursor-pos (rtos (cadr cursor-pos) 2 4) "null")
      "}"
    )
  )
)

(defun cad-obs-log-command-end (reactor-object command-list)
  "Reactor callback for command end."
  (setq cmd-name (car command-list))
  
  (cad-obs-log-entry "COMMAND_END"
    (strcat
      "{"
      "\"command\":" (cad-obs-escape-json cmd-name) ","
      "\"object_count\":" (itoa (cad-obs-object-count))
      "}"
    )
  )
  
  ;; Check for tasks if auto-task is enabled
  (if *CAD-OBS-AUTO-TASK*
    (cad-obs-check-tasks)
  )
)

(defun cad-obs-log-command-cancel (reactor-object command-list)
  "Reactor callback for command cancel."
  (setq cmd-name (car command-list))
  
  (cad-obs-log-entry "COMMAND_CANCEL"
    (strcat
      "{"
      "\"command\":" (cad-obs-escape-json cmd-name)
      "}"
    )
  )
)

(defun cad-obs-log-lisp-start (reactor-object command-list)
  "Reactor callback for LISP command start."
  (setq cmd-name (car command-list))
  
  (cad-obs-log-entry "LISP_START"
    (strcat
      "{"
      "\"function\":" (cad-obs-escape-json cmd-name)
      "}"
    )
  )
)

(defun cad-obs-log-object-added (reactor-object obj-list)
  "Reactor callback when object is added."
  ;; Only log summary to avoid spam
  (cad-obs-log-entry "OBJECT_ADDED"
    (strcat
      "{"
      "\"count\":" (itoa (length obj-list))
      "}"
    )
  )
)

(defun cad-obs-log-layer-change (reactor-object data)
  "Reactor callback for layer changes."
  (cad-obs-log-entry "LAYER_CHANGE"
    (strcat
      "{"
      "\"new_layer\":" (cad-obs-escape-json (cad-obs-get-current-layer))
      "}"
    )
  )
)

;; ------------------------------------------------------------
;; SESSION MANAGEMENT
;; ------------------------------------------------------------

(defun c:CAD-OBSERVER-START ()
  "Start a CAD Observer logging session."
  (if *CAD-OBS-ACTIVE*
    (princ "\n** CAD Observer already running! Use CAD-OBSERVER-STOP first.")
    (progn
      ;; Ensure directories exist
      (cad-obs-ensure-dirs)
      
      ;; Initialize session
      (setq *CAD-OBS-SESSION-ID* (cad-obs-session-id))
      (setq *CAD-OBS-LOG-FILE* 
        (strcat *CAD-OBS-LOG-PATH* "session_" *CAD-OBS-SESSION-ID* ".jsonl"))
      (setq *CAD-OBS-CMD-COUNT* 0)
      (setq *CAD-OBS-ACTIVE* T)
      
      ;; Create reactors
      (setq *CAD-OBS-CMD-REACTOR*
        (vlr-command-reactor nil
          '(
            (:vlr-commandWillStart . cad-obs-log-command)
            (:vlr-commandEnded . cad-obs-log-command-end)
            (:vlr-commandCancelled . cad-obs-log-command-cancel)
          )
        )
      )
      
      (setq *CAD-OBS-LISP-REACTOR*
        (vlr-lisp-reactor nil
          '(
            (:vlr-lispWillStart . cad-obs-log-lisp-start)
          )
        )
      )
      
      ;; Log session start
      (cad-obs-log-entry "SESSION_START"
        (strcat
          "{"
          "\"drawing\":" (cad-obs-escape-json (cad-obs-get-drawing-name)) ","
          "\"layers\":" "[" 
            (apply 'strcat 
              (mapcar '(lambda (x) (strcat (cad-obs-escape-json x) ",")) 
                (cad-obs-get-layers))) 
          "\"\"]"
          "}"
        )
      )
      
      (princ (strcat "\n** CAD Observer Started **"))
      (princ (strcat "\n   Session: " *CAD-OBS-SESSION-ID*))
      (princ (strcat "\n   Log: " *CAD-OBS-LOG-FILE*))
      (princ "\n   Commands: CAD-OBSERVER-STOP, CAD-OBSERVER-STATUS, CAD-OBSERVER-TASK")
    )
  )
  (princ)
)

(defun c:CAD-OBSERVER-STOP ()
  "Stop the CAD Observer logging session."
  (if (not *CAD-OBS-ACTIVE*)
    (princ "\n** CAD Observer is not running.")
    (progn
      ;; Log session end
      (cad-obs-log-entry "SESSION_END"
        (strcat
          "{"
          "\"total_commands\":" (itoa *CAD-OBS-CMD-COUNT*)
          "}"
        )
      )
      
      ;; Remove reactors
      (if *CAD-OBS-CMD-REACTOR*
        (vlr-remove *CAD-OBS-CMD-REACTOR*))
      (if *CAD-OBS-LISP-REACTOR*
        (vlr-remove *CAD-OBS-LISP-REACTOR*))
      
      ;; Clear state
      (setq *CAD-OBS-ACTIVE* nil)
      (setq *CAD-OBS-CMD-REACTOR* nil)
      (setq *CAD-OBS-LISP-REACTOR* nil)
      
      (princ (strcat "\n** CAD Observer Stopped **"))
      (princ (strcat "\n   Commands logged: " (itoa *CAD-OBS-CMD-COUNT*)))
      (princ (strcat "\n   Log saved: " *CAD-OBS-LOG-FILE*))
    )
  )
  (princ)
)

(defun c:CAD-OBSERVER-STATUS ()
  "Show CAD Observer status."
  (princ "\n============ CAD Observer Status ============")
  (if *CAD-OBS-ACTIVE*
    (progn
      (princ "\n  Status: ACTIVE")
      (princ (strcat "\n  Session: " *CAD-OBS-SESSION-ID*))
      (princ (strcat "\n  Commands: " (itoa *CAD-OBS-CMD-COUNT*)))
      (princ (strcat "\n  Log: " *CAD-OBS-LOG-FILE*))
      (princ (strcat "\n  Auto-Task: " (if *CAD-OBS-AUTO-TASK* "ON" "OFF")))
    )
    (princ "\n  Status: INACTIVE")
  )
  (princ "\n=============================================")
  (princ)
)

;; ------------------------------------------------------------
;; TASK EXECUTION (Claude -> AutoCAD)
;; ------------------------------------------------------------

(defun cad-obs-check-tasks ()
  "Check for and execute pending tasks from Claude."
  (setq task-files (vl-directory-files *CAD-OBS-TASK-PATH* "*.json" 1))
  (if task-files
    (foreach task-file task-files
      (cad-obs-execute-task 
        (strcat *CAD-OBS-TASK-PATH* task-file))
    )
  )
)

(defun cad-obs-execute-task (task-path)
  "Execute a single task file."
  (setq file (open task-path "r"))
  (if file
    (progn
      ;; Read entire file
      (setq content "")
      (while (setq line (read-line file))
        (setq content (strcat content line))
      )
      (close file)
      
      ;; Parse task type (simple parsing - look for task_type field)
      (cond
        ;; SCRIPT task - execute AutoCAD script commands
        ((wcmatch content "*\"task_type\":\"script\"*")
          (cad-obs-execute-script-task content task-path))
        
        ;; LISP task - execute LISP code
        ((wcmatch content "*\"task_type\":\"lisp\"*")
          (cad-obs-execute-lisp-task content task-path))
        
        ;; QUERY task - return drawing info to Claude
        ((wcmatch content "*\"task_type\":\"query\"*")
          (cad-obs-execute-query-task content task-path))
        
        ;; Unknown task type
        (T
          (princ (strcat "\n** Unknown task type in: " task-path)))
      )
      
      ;; Move task to done folder
      (setq done-path 
        (strcat *CAD-OBS-DONE-PATH* 
          (vl-filename-base task-path) "_done.json"))
      (vl-file-rename task-path done-path)
    )
  )
)

(defun cad-obs-execute-script-task (content task-path)
  "Execute a script task (AutoCAD commands)."
  ;; Extract commands between "commands":[ and ]
  (setq start-pos (vl-string-search "\"commands\":[" content))
  (if start-pos
    (progn
      (setq cmd-start (+ start-pos 12))
      (setq cmd-end (vl-string-search "]" content cmd-start))
      (setq cmd-str (substr content (1+ cmd-start) (- cmd-end cmd-start)))
      
      ;; Parse command array (simplified - expects "cmd1","cmd2" format)
      (setq cmds (cad-obs-parse-string-array cmd-str))
      
      ;; Execute each command
      (princ "\n** Executing Claude Task **")
      (foreach cmd cmds
        (princ (strcat "\n   > " cmd))
        (command cmd)
      )
      (princ "\n** Task Complete **")
      
      ;; Log task execution
      (cad-obs-log-entry "CLAUDE_TASK"
        (strcat
          "{"
          "\"task_type\":\"script\","
          "\"commands\":" (itoa (length cmds))
          "}"
        )
      )
    )
  )
)

(defun cad-obs-execute-lisp-task (content task-path)
  "Execute a LISP task."
  ;; Extract code between "code":" and next "
  (setq start-pos (vl-string-search "\"code\":\"" content))
  (if start-pos
    (progn
      (setq code-start (+ start-pos 8))
      (setq code-end (vl-string-search "\"" content code-start))
      (setq code-str (substr content (1+ code-start) (- code-end code-start)))
      
      ;; Unescape the code
      (setq code-str (vl-string-subst "\"" "\\\"" code-str))
      (setq code-str (vl-string-subst "\n" "\\n" code-str))
      
      ;; Execute
      (princ "\n** Executing Claude LISP Task **")
      (eval (read code-str))
      (princ "\n** LISP Task Complete **")
      
      ;; Log
      (cad-obs-log-entry "CLAUDE_TASK"
        (strcat
          "{"
          "\"task_type\":\"lisp\""
          "}"
        )
      )
    )
  )
)

(defun cad-obs-execute-query-task (content task-path)
  "Execute a query task - return drawing info to Claude."
  ;; Extract query type
  (setq result-file 
    (strcat *CAD-OBS-LOG-PATH* "query_result_" 
      (rtos (getvar "CDATE") 2 6) ".json"))
  
  (setq out (open result-file "w"))
  (if out
    (progn
      (write-line "{" out)
      (write-line (strcat "\"timestamp\":" (cad-obs-escape-json (cad-obs-timestamp)) ",") out)
      (write-line (strcat "\"drawing\":" (cad-obs-escape-json (cad-obs-get-drawing-name)) ",") out)
      (write-line (strcat "\"current_layer\":" (cad-obs-escape-json (cad-obs-get-current-layer)) ",") out)
      (write-line (strcat "\"object_count\":" (itoa (cad-obs-object-count)) ",") out)
      
      ;; Layer list
      (write-line "\"layers\":[" out)
      (setq layers (cad-obs-get-layers))
      (setq first T)
      (foreach layer layers
        (if (not first) (write-line "," out))
        (write-line (cad-obs-escape-json layer) out)
        (setq first nil)
      )
      (write-line "]," out)
      
      ;; System variables
      (write-line "\"system_vars\":{" out)
      (write-line (strcat "\"DIMSCALE\":" (rtos (getvar "DIMSCALE") 2 4) ",") out)
      (write-line (strcat "\"LTSCALE\":" (rtos (getvar "LTSCALE") 2 4) ",") out)
      (write-line (strcat "\"TEXTSIZE\":" (rtos (getvar "TEXTSIZE") 2 4) ",") out)
      (write-line (strcat "\"INSUNITS\":" (itoa (getvar "INSUNITS"))) out)
      (write-line "}" out)
      
      (write-line "}" out)
      (close out)
      
      (princ (strcat "\n** Query result saved: " result-file))
    )
  )
)

(defun cad-obs-parse-string-array (str)
  "Parse a JSON-style string array into a list."
  ;; Simple parser for ["a","b","c"] format
  (setq result '())
  (setq pos 0)
  (while (setq start (vl-string-search "\"" str pos))
    (setq end (vl-string-search "\"" str (1+ start)))
    (if end
      (progn
        (setq item (substr str (+ start 2) (- end start 1)))
        (setq result (cons item result))
        (setq pos (1+ end))
      )
      (setq pos (strlen str))
    )
  )
  (reverse result)
)

(defun c:CAD-OBSERVER-TASK ()
  "Manually check for and execute Claude tasks."
  (cad-obs-check-tasks)
  (princ)
)

(defun c:CAD-OBSERVER-AUTO ()
  "Toggle automatic task checking after each command."
  (setq *CAD-OBS-AUTO-TASK* (not *CAD-OBS-AUTO-TASK*))
  (princ (strcat "\n** Auto-Task: " (if *CAD-OBS-AUTO-TASK* "ON" "OFF")))
  (princ)
)

;; ------------------------------------------------------------
;; INITIALIZATION
;; ------------------------------------------------------------

(princ "\n============================================")
(princ "\n  CAD Observer Plugin Loaded")
(princ "\n  Commands:")
(princ "\n    CAD-OBSERVER-START  - Start logging")
(princ "\n    CAD-OBSERVER-STOP   - Stop logging")  
(princ "\n    CAD-OBSERVER-STATUS - Show status")
(princ "\n    CAD-OBSERVER-TASK   - Check for Claude tasks")
(princ "\n    CAD-OBSERVER-AUTO   - Toggle auto-task")
(princ "\n============================================")
(princ)
