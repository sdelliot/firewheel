.. _emulytics-introduction:

#####################
Cyber Experimentation
#####################

Many aspects of societal importance such as the economy, our national security, or the smooth operation of our own organizations depend increasingly on complicated computing and communications technologies.
These systems can be vast and their detailed behavior is not well understood, especially in the face of rare or malicious inputs.
Moreover, we incur substantial risk by depending on systems we do not understand.

Researchers, operators, and designers have a variety of tools at their disposal to study large distributed systems.
Traditional mathematical techniques like queuing system models or statistical models are often used to gain large-scale or summary insights about systems constructed from well characterized components.
Mature network and system simulators like `ns-3 <https://www.nsnam.org/>`_ or the `Riverbed Modeler <https://www.riverbed.com/products/riverbed-modeler/>`_ (formerly known as OPNET) are useful when exploring the properties and dynamic behavior of networks that use standard communications and routing protocols like :term:`BGP <Border Gateway Protocol>`, :term:`OSPF <Open Shortest Path First>`, and :term:`STP <Spanning Tree Protocol>` for which reliable simulator implementations exist.

*************************************
The Case for Emulated Experimentation
*************************************

In some important cases, however, our research needs are not easily satisfied by mathematical models or simulators.
For example, distributed systems are often constructed from software building blocks whose individual behavior is itself not well understood or documented.
The collective behavior of such a distributed system is only completely described by its *implementation*.
Simulation or abstract models alone are not good candidates for understanding that kind of system.

Consider Tor [#]_, a large-scale Internet service whose global behavior is an emergent property of the interaction of thousands of instances of different software clients, the network transports they use, and the behavior of its many users and web services they access via Tor.
We simply don't know enough to produce a mathematical model or meaningful simulation that answers many important performance, reliability, and security questions about Tor as it is implemented today and as it continues to evolve.
In the academic literature there have been several attempts to model the Tor network. We will briefly cover a couple of these papers and outline some of the advantages emulation provides over these existing tools.
`Shadow <https://shadow.github.io/>`_ [#]_ is a discrete-event simulator which enables running plugins that can simulate the actual Tor software.
The trade-offs between simulation and emulation are numerous, but in general it is between performance and accuracy.
For example, Shadow uses less computational resources than an emulation environment but has difficulty with multiprocessing applications.
Shadow performed well when it tested a new Tor circuit scheduling algorithm.
However, it would not be able to enable a researcher to understand the security implications of a new cryptographic protocol because it *simulates* Tor's cryptography by introducing CPU delays rather than performing the actual operation.
Fundamentally, each tool is valuable for specific uses, but it is important to understand the trade-offs when selecting a tool.

Alternatively, imagine posing questions about the reliability of the complicated, software-intensive control systems at the heart of a modern manufacturing process or the myriad interlinked databases of a financial system.
These questions depend on software implementation details and how the components interact with one another in response to the inputs they receive, some of which may be exceptionally rare or even malicious.

Careful observation of live versions of these kinds of systems is often the best alternative for understanding their complicated properties and behaviors.
Ideally, one could experiment directly on the operational systems that interest us in their real environments.
Often, however, we are interested in how systems will perform when subjected to unusual, pathological, or malicious inputs.
It is rare to find operators willing to subject their running, working systems to stressful and failure-inducing stimuli so they can understand them better.
For similar reasons, we do not subject healthy people to exploratory surgery or expose them to potentially harmful substances to confirm and catalog their effects.
Further, if we have questions that concern a hypothetical system that does not yet exist, performing live experiments is not even an option.

Experiments built on emulation-based models of computing, network, and control systems are a promising alternative to live experimentation for understanding large, complex, distributed systems.
Such models use some combination of real and emulated components like computers, mobile devices, embedded systems, switches, routers, network links, and control systems to build a laboratory copy of a real or imagined distributed system we want to study.
Because the environment is virtualized, we can often run the exact versions of the distributed system software we are interested in studying.
It is also natural for live people to participate in such virtual environments for training or testing purposes.
Emulation-based models enable us to perform the what-if experiments we are interested in without incurring the expense and risk of experimenting on production systems.

*********
Emulytics
*********

At Sandia, the term "`Emulytics <https://www.sandia.gov/emulytics>`_" refers to the scientific pursuit of the understanding of the behavior of complex, distributed cyber system by using a holistic approach to system emulation and analytics.

Some real-world Emulytics applications have included:

- Testing detection and mitigation techniques at realistic network scales.
- Replicating network attacks and malware behavior in a representative and safe environment.
- Conducting comparative performance analysis on novel architectures and network protocols.
- Performing pre-deployment planning and effectiveness testing of new policies and processes.
- Providing realistic and effective training environments.
- Testing and evaluating the correctness of real systems and devices in a representative virtual environment.
- Answering questions about Internet-scale network services like Tor and I2P.

.. _emulytics-experiments:

Experiments
===========

Designing and executing a good Emulytics experiment is much like experimenting in other domains.
For example, *all* good experiments begin with a *question*.
All experimental activities originate from and are driven by the question.
Once a question has been established, the next step is to design an experiment that can answer, or at least shed light on, the question.
Formulating questions and designing appropriate experiments are crucial steps to getting the most out of an experimental approach to distributed system understanding.
In general, the questions you choose to study and the experiments you design to answer them will be very specific to your problem domain.
Assuming you have a question and have designed an experiment, FIREWHEEL makes it easy to *implement* experiments.

Implementing a good experiment requires an experimenter to have the following four core capabilities:

- **Building** appropriately designed experiments.
- **Controlling** the initial conditions of an experiment reliably.
- **Observing** and recording quantities of interest over the course of an experiment.
- **Analyzing** experimental results and coming to meaningful conclusions about the system of interest.


Good experiments also exhibit the following two important characteristics:

- **Credibility** based on evidence.
- **Economy** of scale and complexity.

FIREWHEEL provides a framework which enables these capabilities and assists a user in answering their research question.

.. [#] Roger Dingledine, Nick Mathewson, and Paul Syverson. 2004. Tor: the second-generation onion router. In Proceedings of the 13th conference on USENIX Security Symposium - Volume 13 (SSYM'04). USENIX Association, USA, 21.

.. [#] Jansen, Rob, and Nicholas Hooper. Shadow: Running Tor in a Box for Accurate and Efficient Experimentation. Network and Distributed System Security Symposium, 2012. https://www.ndss-symposium.org/wp-content/uploads/2017/09/09_3.pdf
